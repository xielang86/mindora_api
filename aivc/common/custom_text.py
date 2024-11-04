from typing import Optional, List
import hashlib
from aivc.config.config import L
import time
from pydantic import BaseModel
from aivc.common.document import Document

class Metadata(BaseModel):
    id: Optional[str] = ""
    source_id: Optional[str] = ""
    article_type: Optional[int] = 1, #1:原创、2:转发、7:评论、8:弹幕、100:文档
    url: Optional[str] = ""
    filename: Optional[str] = ""
    title: Optional[str] = ""
    content: Optional[str] = ""
    channel: Optional[str] = ""
    ctime: Optional[int] = 0
    ctime_str: Optional[str] = ""
    utime: Optional[int] = 0
    utime_str: Optional[str] = ""
    
class CollectionInfo(BaseModel):
    collect_id: Optional[str] = ""
    company_id: Optional[str] = ""
    company_name_clean: Optional[str] = ""
    user_name: Optional[str] = ""
    user_id: Optional[str] = ""

class ProcessingInfo(BaseModel):
    processed_version: Optional[str] = ""
    keywords: Optional[List[str]] = []
    search_score: Optional[float] = 0
    content_embedding: Optional[List[float]] = []
    keywords_embedding: Optional[List[float]] = []

class StorageInfo(BaseModel):
    index: Optional[str] = ""
    id: Optional[str] = ""
    score: Optional[float] = 0
class ParagraphInfo(BaseModel):
    start_offset: Optional[int] = 0
    end_offset: Optional[int] = 0
    paragraph_id: Optional[str] = ""
    next_paragraph_id: Optional[str] = ""
    previous_paragraph_id: Optional[str] = ""
    parent_id: Optional[str] = ""
class CustomText(BaseModel, Document):
    metadata: Optional[Metadata] = None
    collection_info: Optional[CollectionInfo] = None
    processing_info: Optional[ProcessingInfo] = None
    paragraph_info: Optional[ParagraphInfo] = None
    storage_info: Optional[StorageInfo] = None

    def get_source_id(self):
        if self.metadata.source_id == "" or self.metadata.source_id is None:
            return self.metadata.id
        else:
            if self.metadata.id not in self.metadata.source_id.split(","):
                return self.metadata.source_id + "," + self.metadata.id
            else:
                return self.metadata.source_id
    
    def gen_content_hash(self) -> str:
        collect_id = ""
        if self.collection_info:
            collect_id = self.collection_info.collect_id
        return gen_content_hash(collect_id, self.metadata.content)

    def gen_content_hash_v2(self) -> str:
        return gen_content_hash("", self.metadata.content)
    
    def get_time_str(self) -> str:
        if self.metadata.ctime_str:
            return self.metadata.ctime_str
        if not self.metadata.ctime:
            return ""
        return time.strftime("%Y-%m-%d", time.localtime(self.metadata.ctime))

    def get_mapping(self):
        return {
            "properties": {
                "metadata": {
                    "properties": {
                        "id": {
                            "type": "keyword" 
                        },
                        "source_id": { 
                            "type": "keyword"
                        },
                        "article_type": {
                            "type": "keyword"  
                        },
                        "url": {
                            "type": "keyword"  
                        },
                        "filename": {
                            "type": "keyword"
                        },
                        "title": {
                            "type": "text",
                            "analyzer": "ik_max_word"
                        },
                        "content": {
                            "type": "text",
                            "analyzer": "ik_max_word"
                        },
                        "channel": {
                            "type": "keyword"
                        },
                        "ctime": {
                            "type": "integer"
                        },
                        "utime": {
                            "type": "date"
                        }
                    }
                },
                "collection_info": {
                    "properties": {
                        "collect_id": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "company_id": {
                            "type": "keyword"
                        },
                        "company_name_clean": {
                            "type": "keyword" 
                        },
                        "user_name": {
                            "type": "keyword"
                        },
                        "user_id": {
                            "type": "keyword"
                        }
                    }
                },
                "processing_info": {
                    "properties": {
                        "processed_version": {
                            "type": "keyword"
                        },
                        "keywords": {
                            "type": "text",
                            "analyzer": "ik_max_word"
                        },
                        "search_score": {
                            "type": "float"
                        }
                    }
                },
                "paragraph_info": {
                    "properties": {
                        "start_offset": {
                            "type": "integer"
                        },
                        "end_offset": {
                            "type": "integer"
                        },  
                        "paragraph_id": {
                            "type": "keyword"
                        },
                        "next_paragraph_id": {
                            "type": "keyword"
                        },
                        "previous_paragraph_id": {
                            "type": "keyword"
                        },
                        "parent_id": {
                            "type": "keyword" 
                        }
                    }
                },
                "content_embedding": {
                    "properties": {
                        "predicted_value": {
                            "type": "dense_vector",
                            "dims": 1024,   
                            "index": True,
                            "similarity": "cosine"
                        }
                    }
                },
                "keywords_embedding": {
                    "properties": {
                        "predicted_value": {
                            "type": "dense_vector",
                            "dims": 1024,   
                            "index": True,
                            "similarity": "cosine"
                        }
                    }
                }
            }
        }

def gen_content_hash(collect_id: str, content: str) -> str:
    content_string = f"{collect_id}{content}"
    content_hash = hashlib.sha256(content_string.encode('utf-8')).hexdigest()
    return content_hash

class CustomTextParam(BaseModel):
    vs_id: str
    filename: str
    text: str
    split: str
    keywords: str
    index: Optional[str] = ""
    clean: Optional[str] = None
    search: Optional[str] = None
    desc: Optional[str] = None
    

def parse_search_response_safe(search_response: dict) -> List[CustomText]:
    news_list = []
    try:
        if search_response is None:
            return news_list
        search_results = search_response.get("hits", {}).get("hits", [])
    except Exception as e:
        # search_response 或 search_response.get("hits") 不是一个字典
        L.error(f"parse_search_response_safe search_response error:{e}")
        return news_list

    for result in search_results:
        try:
            ct = parse_source(result)
            news_list.append(ct)
        except Exception as e:
            L.error(f"parse_search_response_safe result error:{e}")
    return news_list

def parse_source(result: dict) -> CustomText:
    source = result.get('_source')
    if source is None:
        return None
    ctime = source.get('metadata', {}).get('ctime', 0)
    ctime, ctime_str = parse_time(ctime)
    utime = source.get('metadata', {}).get('utime', 0)
    utime, utime_str = parse_time(utime)
    
    ct = CustomText(
    metadata=Metadata(
            id=result.get('_id'),
            source_id=source.get('metadata', {}).get('source_id', ''),
            article_type=source.get('metadata', {}).get('article_type', ''),
            url=source.get('metadata', {}).get('url', ''),
            filename=source.get('metadata', {}).get('filename', ''),
            title=source.get('metadata', {}).get('title', ''),
            content=source.get('metadata', {}).get('content', ''),
            channel=source.get('metadata', {}).get('channel', ''),
            ctime=ctime,
            ctime_str=ctime_str,
            utime=utime,
            utime_str=utime_str
        ),
        collection_info=CollectionInfo(
            collect_id=source.get('collection_info', {}).get('collect_id', ''),
            company_id=source.get('collection_info', {}).get('company_id', ''),
            company_name_clean=source.get('collection_info', {}).get('company_name_clean', ''),
            user_name=source.get('collection_info', {}).get('user_name', ''),
            user_id=source.get('collection_info', {}).get('user_id', '')
        ),
        processing_info=ProcessingInfo(
            processed_version=source.get('processing_info', {}).get('processed_version', ''),
            keywords=source.get('processing_info', {}).get('keywords', []),
            search_score=result.get('_score')
        ),
        paragraph_info=ParagraphInfo(
            start_offset=source.get('paragraph_info', {}).get('start_offset', 0),
            end_offset=source.get('paragraph_info', {}).get('end_offset', 0),
            paragraph_id=source.get('paragraph_info', {}).get('paragraph_id', ''),
            parent_id=source.get('paragraph_info', {}).get('parent_id', ''),
            next_paragraph_id=source.get('paragraph_info', {}).get('next_paragraph_id', ''),
            previous_paragraph_id=source.get('paragraph_info', {}).get('previous_paragraph_id', '')
        ),
        storage_info=StorageInfo(
            index=result.get('_index'),
            id=result.get('_id'),
            score=result.get('_score')
        ),
    )
    return ct

def parse_time(time_input):
    time_str = ""
    if isinstance(time_input, int):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_input))
        return time_input, time_str
    if isinstance(time_input, str):
        time_str = time_input
        return int(time.mktime(time.strptime(time_str, '%Y-%m-%dT%H:%M:%S%z'))), time_str
    return 0, time_str

def parse_search_response_v7_news(search_response: dict) -> List[CustomText]:
    news_list = []
    if search_response is None or isinstance(search_response, dict) is False:
        return news_list
    
    try:
        search_results = search_response.get("hits", {}).get("hits", [])
    except Exception as e:
        import traceback
        L.error(f"parse_search_response_safe search_response error:{e} stack_trace:{traceback.format_exc()} search_response:{search_response}")
        return news_list

    for result in search_results:
        source = result.get('_source')
        if source is not None:
            ctime=source.get('ctime', 0)
            utime = ctime
            ctime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ctime))
            utime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(utime))
            news = CustomText(
            metadata=Metadata(
                    id=result.get('_id'),
                    article_type=source.get('wtype', 1),
                    url=source.get('url', ''),
                    filename=source.get('filename', ''),
                    title=source.get('title', ''),
                    content=source.get('content', ''),
                    channel=source.get('channel', ''),
                    ctime=ctime,
                    ctime_str=ctime_str,
                    utime=utime,
                    utime_str=utime_str
                ),
                storage_info=StorageInfo(
                    index=result.get('_index'),
                    id=result.get('_id'),
                    score=result.get('_score')
                ),
            )
            news_list.append(news)
    return news_list

def unique_by_url(custom_texts: List[CustomText]):
    seen_urls = set()
    unique_texts = []
    for custom_text in custom_texts:
        url = custom_text.metadata.url
        if url not in seen_urls:
            seen_urls.add(url)
            unique_texts.append(custom_text)
    return unique_texts

if __name__ == "__main__":
    p = CustomTextParam(vs_id="1", filename="test.txt", text="test", split="test", keywords="test")
    print(p.__dict__)