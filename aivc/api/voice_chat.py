from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
import os
from typing import Optional,AsyncGenerator
from aivc.srt.manager import SRTManager, SRTType
from aivc.utils.id import get_id
from aivc.srt.common import SRTRsp
from aivc.config.config import L,CANCELLATION_EVENTS, settings
from aivc.chat.chat import Chat
from aivc.common.trace_tree import TraceTree,TraceSRT,TraceTTS,TraceTTSResp
from aivc.tts.manager import TTSManager
from aivc.tts.common import TTSRsp
from aivc.utils.audio import calculate_pcm_duration
import asyncio
import traceback
from aivc.common.chat import Req, VCReqData, Resp, VCRespData, ContentType, HandlerResult, ConverMsg
import base64
import time
from aivc.common.route import Route
from aivc.common.query_analyze import QueryAnalyzer
from aivc.chat.router import Router
from aivc.common.kb import KBSearchResult
from aivc.common.task_class import QuestionType
from aivc.chat.song import SongPlayer
from aivc.chat.sound import ActionSound,AudioFormat
from aivc.chat import conversation
from aivc.chat.keyword_replace import KeywordReplacer
from aivc.chat.meaning_less import MeaninglessWords
from aivc.data.db.trace_log import save_trace
from aivc.data.db.pg_engine import engine
from sqlmodel import Session
from aivc.chat.prompt_selector import PromptTemplate
from aivc.utils.weather import WeatherService
from datetime import datetime
from aivc.chat.message_manager import MessageManager
from aivc.common.file import save_upload_file,validate_audio_file_size
from aivc.api.cmd_params import CmdParamsManager

router = APIRouter()

async def process_voice_conversation(
    file_path: str,
    trace_sn: str,
    audio_queue: asyncio.Queue,
    cancellation_event: asyncio.Event,
    trace_tree:TraceTree = TraceTree(),
    req: Req[VCReqData] = None):

    try:
        chat_instance = Chat(content_type=req.data.content_type)
        result = None
        if req.data.content_type == ContentType.IMAGE.value:
            result = await image_handler(
                file_path=file_path,
                trace_sn=trace_sn,
                audio_queue=audio_queue,
                cancellation_event=cancellation_event,
                trace_tree=trace_tree,
                req=req,
                chat_instance=chat_instance)
        
        if req.data.content_type in [ContentType.AUDIO.value, ContentType.TEXT.value]:
            result = await audio_handler(
                file_path=file_path,
                trace_sn=trace_sn,
                audio_queue=audio_queue,
                cancellation_event=cancellation_event,
                trace_tree=trace_tree,
                req=req,
                chat_instance=chat_instance)
            
        # 保存对话
        L.debug(f"voice_chat result:{result} trace_sn:{trace_sn}")
        if  result and result.question and result.answer:
            await asyncio.to_thread(
                conversation.save_conversation, 
                trace_tree.root.conversation_id, 
                result.question, 
                result.answer,
                question_type=result.question_type)
        await audio_queue_put(audio_queue,None,trace_tree)
    except Exception as e:
        L.error(f"process_audio unexpected error trace_sn:{trace_sn} error:{e} stack:{traceback.format_exc()}")
        resp = TTSRsp(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e))  
        await audio_queue_put(audio_queue,resp,trace_tree)
    finally:
        if result and not trace_tree.srt.text:
            trace_tree.srt.text = result.question
        if result and not trace_tree.llm.answer:
            trace_tree.llm.answer = result.answer
        trace_tree.root.srt_cost = trace_tree.srt.cost
        trace_tree.root.llm_first_cost = trace_tree.llm.first_cost
        trace_tree.root.tts_first_cost = trace_tree.tts.first_cost
        L.debug(f"trace_tree: {trace_tree}")
        CANCELLATION_EVENTS.pop(trace_sn, None)
        
        def save_trace_with_session():
            with Session(engine) as session:
                save_trace(session, trace_tree)
        await asyncio.to_thread(save_trace_with_session)

async def audio_queue_put(audio_queue: asyncio.Queue,resp: TTSRsp, trace_tree:TraceTree):
    if resp and resp.code != 0:
        trace_tree.root.err_code = resp.code
        trace_tree.root.err_message = resp.message
    if resp and resp.code == 0 and resp.stream_seq != -1:
        audio_file = os.path.basename(resp.audio_path) if resp.audio_path else None
        trace_tree.tts.resp_list.append(
            TraceTTSResp(
                text = resp.text,
                audio_filename = resp.audio_filename,
                action_params = resp.action_params,
                audio_file = audio_file,
                audio_file_size = resp.output_length,
                cost = resp.cost,
                stream_seq = resp.stream_seq
            ))
    await audio_queue.put(resp)

async def image_handler(
    file_path: str,
    trace_sn: str,
    audio_queue: asyncio.Queue,
    cancellation_event: asyncio.Event,
    trace_tree:TraceTree = TraceTree(),
    req: Req[VCReqData] = None,
    chat_instance:Chat = None) -> HandlerResult:
    # 图像识别
    question = PromptTemplate.VISIO_PROMPT

    # 从对话中获取上一次问题
    if req and req.conversation_id:
        conversation_id = req.conversation_id
        last_question = await asyncio.to_thread(
                conversation.get_last_take_photo_question,
                conversation_id=conversation_id
            )
        L.debug(f"gen_messages conversation_id:{conversation_id} last_question:{last_question}")
        if last_question:
            question = PromptTemplate.VISIO_PROMPT_V2.format(
                question=last_question)
    L.debug(f"image_handler gen_messages question:{question}")
    
    answer = await llm_and_tts(
                question=question,
                trace_sn=trace_sn,
                audio_queue=audio_queue,
                cancellation_event=cancellation_event,
                trace_tree=trace_tree,
                req=req,
                file_path=file_path,
                chat_instance=chat_instance)
    return HandlerResult(
            question=question, 
            answer=answer, 
            question_type=QuestionType.PHOTO_RECOGNITION.value)

async def audio_handler(
    file_path: str,
    trace_sn: str,
    audio_queue: asyncio.Queue,
    cancellation_event: asyncio.Event,
    trace_tree:TraceTree = TraceTree(),
    req: Req[VCReqData] = None,
    chat_instance:Chat = None) -> HandlerResult:

    req_text = ""
    if req.data.content_type == ContentType.TEXT.value:
        req_text = req.data.content

    # 语音识别
    if req.data.content_type == ContentType.AUDIO.value:
        srt = SRTManager.create_srt(srt_type=SRTType.XUNFEI)
        srt_rsp: SRTRsp = await srt.recognize(audio_path=file_path, message_id=trace_sn)
        
        trace_srt = TraceSRT(
            cost=srt_rsp.cost,
            code=srt_rsp.code,
            message=srt_rsp.message,
            text=srt_rsp.text)
        trace_tree.srt = trace_srt

        if srt_rsp.code != 0:
            L.error(f"voice_chat srt error trace_sn:{trace_sn} code:{srt_rsp.code} message:{srt_rsp.message}")
            rsp = TTSRsp(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=srt_rsp.message)
            await audio_queue_put(audio_queue,rsp,trace_tree)
            return None
        L.debug(f"voice_chat srt success trace_sn:{trace_sn} text:{srt_rsp.text} cost:{srt_rsp.cost}")
        if len(srt_rsp.text.strip()) == 0:
            L.error(f"voice_chat识别不到有效内容, trace_sn:{trace_sn}")
            rsp = TTSRsp(
                code=status.HTTP_400_BAD_REQUEST,
                message="识别不到有效内容")
            await audio_queue_put(audio_queue,rsp,trace_tree)
            return None
        req_text = srt_rsp.text

    if MeaninglessWords().is_meaningless(req_text.strip()):
        L.error(f"voice_chat识别到无意义内容, trace_sn:{trace_sn}")
        rsp = TTSRsp(
            code=status.HTTP_400_BAD_REQUEST,
            message="无意义内容",
            text=req_text)
        await audio_queue_put(audio_queue,rsp,trace_tree)
        return

    # 更新进MessageManager
    ts = datetime.now().isoformat()
    client_addr = ""
    if trace_tree and trace_tree.root and trace_tree.root.client_addr:
        client_addr = trace_tree.root.client_addr
    await MessageManager().insert_message(conversation_id = req.conversation_id,
                                    message = ConverMsg(
                                        method = req.method,
                                        conversation_id = req.conversation_id,
                                        conversation_id_ts = ts,
                                        message_id = req.message_id,
                                        message_id_ts = ts,
                                        client_addr = client_addr
                                    ))

    # 问题预处理
    router_start_time = time.perf_counter()
    route = Route(
        query_analyzer=QueryAnalyzer(
            question=req_text
        )    
    )
    await Router(route=route,
                chat_instance=chat_instance).router()
    L.debug(f"voice_chat route trace_sn:{trace_sn} question:{req_text} kb_result:{route.kb_result} cost:{int((time.perf_counter() - router_start_time) * 1000)}ms")
    if route and route.kb_result:
        trace_tree.qpp.question_category = route.kb_result.category_name
        if route.kb_result.answer:
            trace_tree.llm.answer = route.kb_result.answer

    question = req_text
    answer = ""
    if isinstance(route.kb_result, KBSearchResult):
        L.debug(f"voice_chat kb_result trace_sn:{trace_sn} category_name:{route.kb_result.category_name}")
        cmd_manager = CmdParamsManager.get_instance()
        if QuestionType.is_cmd_by_value(route.kb_result.category_name):
            # 设备控制命令
            action_param = cmd_manager.get_action_params(
                question_type_value = route.kb_result.category_name,
                params=route.kb_result.params)
            text, audio_filename = cmd_manager.get_cmd_response(route.kb_result.category_name)
            rsp = TTSRsp(
                action="cmd",
                action_params=action_param,
                text=text,
                audio_filename = audio_filename,
                audio_path = None,
                output_length=0,
                audio_data= None,
                audio_format= None,
                stream_seq=1)
            await audio_queue_put(audio_queue,rsp,trace_tree)
            # 发送结束标记
            await audio_queue_put(audio_queue,TTSRsp(stream_seq=-1),trace_tree)
        elif route.kb_result.category_name == QuestionType.SONG.value:
            song_file = SongPlayer().get_next_song(username=trace_tree.root.client_addr)
            song_name = os.path.splitext(os.path.basename(song_file))[0]
            L.debug(f"voice_chat song trace_sn:{trace_sn} song_file:{song_file} song_name:{song_name}")
            answer = f"让我们一起听: {song_name}"

            # 前导音频
            start_time = time.perf_counter()
            tts = TTSManager.create_tts(trace_sn=trace_sn)
            tts_audio_format = AudioFormat.MP3.value
            tts_rsp: TTSRsp = await tts.tts(text=answer,
                                            audio_format=tts_audio_format)
            L.debug(f"tts done trace_sn:{trace_sn} tts cost:{int((time.perf_counter() - start_time) * 1000)}ms tts_rsp.code:{tts_rsp.code}")
            tts_rsp.stream_seq = 1 
            await audio_queue_put(audio_queue,tts_rsp,trace_tree)

            # mp3 音频
            with open(song_file, 'rb') as audio_file:
                audio_data =  audio_file.read()
                rsp = TTSRsp(
                    text=song_name,
                    audio_data=audio_data,
                    audio_format="mp3",
                    audio_path=song_file,
                    output_length=len(audio_data),
                    stream_seq=2)
                await audio_queue_put(audio_queue,rsp,trace_tree)
            # 发送结束标记
            await audio_queue_put(audio_queue,TTSRsp(stream_seq=-1),trace_tree)
        elif route.kb_result.category_name == QuestionType.TAKE_PHOTO.value:
            # 拍照, 不发音频
            sound_info = ActionSound().get_sound_info(
                action=QuestionType.TAKE_PHOTO.value,
                format=req.data.tts_audio_format)
            answer = sound_info.text
            rsp = TTSRsp(
                action=QuestionType.TAKE_PHOTO.value,
                text=sound_info.text,
                audio_path = None,
                output_length=0,
                audio_data= None,
                audio_format= None,
                stream_seq=1)
            await audio_queue_put(audio_queue,rsp,trace_tree)
            # 发送结束标记
            await audio_queue_put(audio_queue,TTSRsp(stream_seq=-1),trace_tree)
        elif route.kb_result.category_name == QuestionType.SLEEP_ASSISTANT.value:
            sound_info = ActionSound().get_sound_info(
                action=QuestionType.SLEEP_ASSISTANT.value,
                format=AudioFormat.MP3.value)
            answer = sound_info.text            
            rsp = TTSRsp(
                action=QuestionType.SLEEP_ASSISTANT.value,
                text=answer,
                audio_path = None,
                output_length=0,
                audio_data= None,
                audio_format= None,
                stream_seq=1)
            await audio_queue_put(audio_queue,rsp,trace_tree)
            # 发送结束标记
            await audio_queue_put(audio_queue,TTSRsp(stream_seq=-1),trace_tree)
        elif route.kb_result.category_name == QuestionType.WEATHER.value:
            question_rag = ""
            try:
                # 获取经纬度
                start_time = time.perf_counter()
                location = await WeatherService().get_location(
                    question = question,
                    ip = trace_tree.root.client_addr.split(":")[0])

                location_cost = int((time.perf_counter() - start_time) * 1000)

                # 获取天气
                start_time = time.perf_counter()
                weath = await WeatherService().get_weather(lon=location.lon,lat=location.lat)
                L.debug(f"voice_chat weather trace_sn:{trace_sn} location:{location} weath:{weath} get_location cost:{location_cost}ms get_weather cost:{int((time.perf_counter() - start_time) * 1000)}ms")
                
                # 生成question
                question_rag = f"今天是{datetime.now().strftime('%Y年%m月%d日')} 天气预报如下: {weath} 根据已知信息，回答如下问题: {question}"
            except Exception as e:
                L.error(f"voice_chat weather error trace_sn:{trace_sn} error:{e} stack:{traceback.format_exc()}")
                question_rag = question

            answer = await llm_and_tts(
                question=question_rag,
                trace_sn=trace_sn,
                audio_queue=audio_queue,
                cancellation_event=cancellation_event,
                trace_tree=trace_tree,
                req=req,
                route=route,
                chat_instance=chat_instance)
        else:
            # 知识库回答
            answer = route.kb_result.answer
            llm_rsp_trunk = route.kb_result.answer
            
            # 处理 TTS
            start_time = time.perf_counter()
            tts = TTSManager.create_tts(trace_sn=trace_sn)
            tts_audio_format = AudioFormat.MP3.value
            tts_rsp: TTSRsp = await tts.tts(text=llm_rsp_trunk,
                                            audio_format=tts_audio_format)
            L.debug(f"tts done trace_sn:{trace_sn} tts cost:{int((time.perf_counter() - start_time) * 1000)}ms tts_rsp.code:{tts_rsp.code}")
            tts_rsp.stream_seq = 1  # 只有一个流
            
            if tts_rsp.code != 0:
                L.error(f"tts error trace_sn:{trace_sn} code:{tts_rsp.code} message:{tts_rsp.message} audio_data len:{len(tts_rsp.audio_data)}")
                rsp = TTSRsp(
                    code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=tts_rsp.message)
                await audio_queue_put(audio_queue,rsp,trace_tree)
                return None
            
            # 放入音频数据
            await audio_queue_put(audio_queue,tts_rsp,trace_tree)
            
            # 发送结束标记
            rsp = TTSRsp(
                stream_seq=-1)
            await audio_queue_put(audio_queue,rsp,trace_tree)
    else:
        answer = await llm_and_tts(
            question=question,
            trace_sn=trace_sn,
            audio_queue=audio_queue,
            cancellation_event=cancellation_event,
            trace_tree=trace_tree,
            req=req,
            route=route,
            chat_instance=chat_instance)
    return HandlerResult(
            question=question, 
            answer=answer, 
            question_type=route.kb_result.category_name if route and route.kb_result else None)

async def llm_and_tts(
    question: str,
    trace_sn: str,
    audio_queue: asyncio.Queue,
    cancellation_event: asyncio.Event,
    trace_tree:TraceTree = TraceTree(),
    req: Req[VCReqData] = None,
    file_path: str = None,
    route:Route = None,
    chat_instance:Chat = None) -> str:
    answer = ""
    llm_start_time = time.perf_counter()
    llm_index = 0
    async for llm_rsp_trunk in chat_instance.chat_stream_by_sentence(
            question=question,
            trace_tree=trace_tree,
            file_path=file_path,
            req=req,
            route=route):
        if llm_index == 0:
            trace_tree.llm.first_cost = int((time.perf_counter() - llm_start_time) * 1000)
        
        # 是否是最新的请求
        is_latest, latest_id = await MessageManager().is_latest_message(req.conversation_id, req.message_id)
        if not is_latest:
            L.debug(f"MessageManager llm_and_tts drop message conversation_id: {req.conversation_id} message_id: {req.message_id}, latest_id: {latest_id}")
            rsp = TTSRsp(
            stream_seq=-1)
            await audio_queue_put(audio_queue,rsp,trace_tree) 
            break


        # 流结束
        if llm_rsp_trunk is None:
            L.debug(f"chat_stream_by_sentence done trace_sn:{trace_sn} llm_index:{llm_index} llm_rsp_trunk:{llm_rsp_trunk}")
            rsp = TTSRsp(
                stream_seq=-1)
            await audio_queue_put(audio_queue,rsp,trace_tree)
            break

        # 对答案进行过滤
        llm_rsp_trunk_clean = KeywordReplacer().replace(llm_rsp_trunk)
        if llm_rsp_trunk_clean != llm_rsp_trunk:
            L.debug(f"chat_stream_by_sentence KeywordReplacer trace_sn:{trace_sn} llm_rsp_trunk:{llm_rsp_trunk} llm_rsp_trunk_clean:{llm_rsp_trunk_clean}")
        
        answer += llm_rsp_trunk_clean
        llm_index += 1
        L.debug(f"chat_stream_by_sentence trace_sn:{trace_sn} llm_rsp_trunk_clean:{llm_rsp_trunk_clean}")
        
        # 检查是否需要中断
        if cancellation_event.is_set():
            L.info(f"voice_chat cancelled during processing trace_sn:{trace_sn}")
            break
        
        tts = TTSManager.create_tts(trace_sn=trace_sn)
        tts_audio_format = AudioFormat.MP3.value
        tts_rsp: TTSRsp = await tts.tts(text=llm_rsp_trunk_clean,
                                        audio_format=tts_audio_format)
        # 流状态
        tts_rsp.stream_seq = llm_index
        L.debug(f"tts done trace_sn:{trace_sn} tts_rsp:{tts_rsp} llm_index:{llm_index}")

        if llm_index == 1:
            trace_tree.tts = TraceTTS(first_cost=tts_rsp.cost)
            
        if tts_rsp.code != 0:
            L.error(f"tts error trace_sn:{trace_sn} code:{tts_rsp.code} message:{tts_rsp.message} audio_data len:{len(tts_rsp.audio_data)}")
            continue
        
        # 等待队列有空位，再放入音频数据
        await audio_queue_put(audio_queue,tts_rsp,trace_tree)
    return answer

async def voice_chat_ws(req: Req[VCReqData], trace_tree:TraceTree = None) -> AsyncGenerator[Resp, None]:
    file_path = ""
    if req.data.content_type in [ContentType.IMAGE.value, ContentType.AUDIO.value]:
        data_bytes = base64.b64decode(req.data.content)
        try:
            file_path = await save_upload_file(data_bytes, req.message_id)
            await validate_audio_file_size(file_path)
        except Exception as e:
            L.error(f"voice_chat HTTPException conversation_id:{req.conversation_id} message_id:{req.message_id} error:{e} stack:{traceback.format_exc()}")
            raise
        L.debug(f"voice_chat save file file_path:{file_path} conversation_id:{req.conversation_id} message_id:{req.message_id}")

    # 最大未消费数据为3
    audio_queue: asyncio.Queue[TTSRsp] = asyncio.Queue(maxsize=settings.AUDIO_QUEUE_MAXSIZE)

    # 取消事件
    cancellation_event = asyncio.Event()
    CANCELLATION_EVENTS[req.conversation_id] = cancellation_event

    async def process_voice_conversation_wrapper():
        try:
            await process_voice_conversation(
                file_path=file_path, 
                trace_sn=req.message_id, 
                audio_queue=audio_queue, 
                cancellation_event=cancellation_event, 
                trace_tree=trace_tree,
                req=req)
        except Exception as e:
            L.error(f"process_voice_conversation_wrapper error conversation_id:{req.conversation_id} message_id:{req.message_id} error:{e} stack:{traceback.format_exc()}")
            resp = TTSRsp(
                code=status.HTTP_400_BAD_REQUEST,
                message=str(e))
            await audio_queue_put(audio_queue,resp,trace_tree)

    async def send_audio_generator() -> AsyncGenerator[Resp, None]:
        try:
            while True:
                tts_rsp = await audio_queue.get()
                if tts_rsp is None:
                    L.debug(f"send_audio_generator rsp is none. conversation_id:{req.conversation_id} message_id:{req.message_id}")
                    break

                # 错误返回到客户端
                if tts_rsp.code != 0:
                    L.error(f"send_audio_generator got error code:{tts_rsp.code} message:{tts_rsp.message} conversation_id:{req.conversation_id} message_id:{req.message_id}")
                    resp = Resp(
                        version=req.version,
                        method=req.method,
                        conversation_id=req.conversation_id,
                        message_id=req.message_id,
                        code=tts_rsp.code,
                        message=tts_rsp.message)
                    yield resp
                    break
                
                audio_data_base64 = None
                if tts_rsp.audio_data:
                    audio_data_base64 = base64.b64encode(tts_rsp.audio_data).decode("utf-8")
                    L.debug(f"send_audio_generator conversation_id:{req.conversation_id} message_id:{req.message_id} audio_data_base64 len:{len(audio_data_base64)} tts_rsp:{tts_rsp}")

                resp_data = VCRespData(
                        action=tts_rsp.action,
                        action_params=tts_rsp.action_params,
                        text=tts_rsp.text,
                        audio_filename=tts_rsp.audio_filename,
                        audio_format=tts_rsp.audio_format,
                        audio_data=audio_data_base64,
                        stream_seq=tts_rsp.stream_seq,
                        sample_rate=tts_rsp.sample_rate,
                        channels=tts_rsp.channels,
                        sample_format=tts_rsp.sample_format,
                        bitrate=tts_rsp.bitrate)
                resp = Resp(
                    version=req.version,
                    method=req.method,
                    conversation_id=req.conversation_id,
                    message_id=req.message_id,
                    data=resp_data)
                yield resp

                # if tts_rsp.audio_format == "pcm":
                #     duration = calculate_pcm_duration(buffer=tts_rsp.audio_data)
                #     await asyncio.sleep(duration-0.4)
        except asyncio.CancelledError:
            L.warning(f"audio_generator cancelled for conversation_id:{req.conversation_id} message_id:{req.message_id}")
            cancellation_event.set()
        finally:
            cancellation_event.set()
            CANCELLATION_EVENTS.pop(req.message_id, None)

    asyncio.create_task(process_voice_conversation_wrapper())
    async for resp in send_audio_generator():
        yield resp

@router.post("/voice-chat")
async def voice_chat(
    file: UploadFile = File(..., description="上传的音频文件"),
    trace_sn: Optional[str] = Form(None, description="追踪标识，若未提供则自动生成")
):
    """
    接口：通过上传的音频文件进行识别（POST请求）
    参数：
        - file (UploadFile): 上传的音频文件（必填）
        - trace_sn (str, 可选): 追踪标识，若未提供则自动生成
    返回：
        StreamingResponse，流式返回语音回复
    """
    trace_sn = trace_sn or get_id()
    content = await file.read()
    try:
        file_path = await save_upload_file(content, trace_sn)
        await validate_audio_file_size(file_path)
    except Exception as e:
        L.error(f"voice_chat HTTPException trace_sn:{trace_sn} error:{e} stack:{traceback.format_exc()}")
        raise
    L.debug(f"voice_chat save file file_path:{file_path} trace_sn:{trace_sn}")

    # 最大未消费数据为3
    audio_queue = asyncio.Queue(maxsize=settings.AUDIO_QUEUE_MAXSIZE)

    # 取消事件
    cancellation_event = asyncio.Event()
    CANCELLATION_EVENTS[trace_sn] = cancellation_event

    async def send_audio_generator() -> AsyncGenerator[bytes, None]:
        try:
            while True:
                audio_data = await audio_queue.get()
                if audio_data is None:
                    break
                yield audio_data
                duration = calculate_pcm_duration(buffer=audio_data)
                await asyncio.sleep(duration)
        except asyncio.CancelledError:
            L.warning(f"audio_generator cancelled for trace_sn:{trace_sn}")
            cancellation_event.set()
        finally:
            cancellation_event.set()
            CANCELLATION_EVENTS.pop(trace_sn, None)

    async def process_voice_conversation_wrapper_post():
        try:
            await process_voice_conversation(file_path, trace_sn, audio_queue, cancellation_event)
        except Exception as e:
            L.error(f"process_voice_conversation_wrapper error trace_sn:{trace_sn} error:{e} stack:{traceback.format_exc()}")
            rsp = TTSRsp(
                code=status.HTTP_400_BAD_REQUEST,
                message=str(e))
            await audio_queue.put(rsp)

    asyncio.create_task(process_voice_conversation_wrapper_post())

    return StreamingResponse(
        send_audio_generator(),
        media_type="audio/x-pcm",
        headers={
            "Content-Type": "audio/x-pcm",
            "Sample-Rate": "16000",
            "Channels": "1",
            "Sample-Format": "S16LE",
            "Bitrate": "256000"
        }
    )

### 取消任务的 RESTful Endpoint ###
@router.post("/cancel-voice-chat")
async def cancel_voice_chat(trace_sn: str):
    """
    取消指定 trace_sn 的 voice_chat 任务
    """
    cancellation_event = CANCELLATION_EVENTS.get(trace_sn)
    if cancellation_event:
        cancellation_event.set()
        return {"detail": f"已取消 trace_sn: {trace_sn} 的任务"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"没有找到 trace_sn: {trace_sn} 对应的任务"
        )