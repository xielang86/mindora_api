import asyncio
import websockets
from aivc.common.chat import VCMethod, Req, VCReqData, Resp, VCRespData
from aivc.utils.audio import audio_file_to_base64
from datetime import datetime
import pytz

async def send_request(websocket, req: Req):
    await websocket.send(req.model_dump_json())
    while True:
        response = await websocket.recv()
        rsp = Resp[VCRespData].model_validate_json(response)
        print(f"Received response: {len(rsp.data.audio_data)}")

async def main():
    uri = "ws://114.55.90.104:9001/ws"  
    async with websockets.connect(uri) as websocket:
        print(f"Connected to WebSocket server: {uri}")

        filename = "/usr/local/src/seven_ai/aivoicechat/upload/20241030-092740-3ef6e7dc-96db-4860-ba4a-099b5f821f94"

        req_data = VCReqData(audio_data=audio_file_to_base64(filename))
        req = Req(
            version="1.0",
            method=VCMethod.VOICE_CHAT,
            conversation_id="conversation_id",
            message_id="message_id",
            token="token",
            timestamp=get_rfc3339_with_timezone(),
            data=req_data
        )

        await send_request(websocket, req)

def get_rfc3339_with_timezone():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz).isoformat()

if __name__ == "__main__":
    asyncio.run(main())
