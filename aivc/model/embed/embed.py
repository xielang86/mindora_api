from sentence_transformers import SentenceTransformer
from sentence_transformers.quantization import quantize_embeddings
from typing import List, Optional, Dict
import numpy as np
from aivc.config.config import settings, L
import time
import os
import psutil
import gc
import torch


class EmbedModel:
    V1 = 'V1'
    V2 = 'V2'

    models: Dict[str, SentenceTransformer] = {}
    
    def __init__(self, version:Optional[str]=None):
        # 设置离线环境变量，确保不连接网络
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        os.environ['HF_HUB_OFFLINE'] = '1'
        
        # self._load_model(EmbedModel.V1, settings.EMBEDDING_MODEL_V1)
        self._load_model(EmbedModel.V2, settings.EMBEDDING_MODEL_V2)
        self.default_version = version if version is not None else EmbedModel.V2

    def _load_model(self, version: str, model_name: str):
        if version not in EmbedModel.models:
            start_time = time.time()
            
            # 强制垃圾回收，获取更准确的基线内存
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # 记录加载前的内存使用
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            try:
                # 检查模型路径是否存在，并且包含必要的模型文件
                if os.path.exists(model_name) and self._is_valid_model_path(model_name):
                    L.info(f"Loading embedding model {version} from local path: {model_name}")
                    EmbedModel.models[version] = SentenceTransformer(
                        model_name, 
                        trust_remote_code=True,
                        local_files_only=True,
                    )
                    
                    # 再次强制垃圾回收
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    
                    # 记录加载后的内存使用
                    memory_after = process.memory_info().rss / 1024 / 1024  # MB
                    memory_used = memory_after - memory_before
                    
                    # 获取模型参数信息
                    model = EmbedModel.models[version]
                    param_count = sum(p.numel() for p in model.parameters())
                    param_size_mb = sum(p.numel() * p.element_size() for p in model.parameters()) / 1024 / 1024
                    
                    L.info(f"EmbedModel {version} loaded successfully.")
                    L.info(f"  Model parameters: {param_count:,} ({param_size_mb:.2f} MB)")
                    L.info(f"  Process memory increase: {memory_used:.2f} MB")
                    L.info(f"  Total process memory: {memory_after:.2f} MB")
                    
                    # 如果使用GPU，也记录GPU内存
                    if torch.cuda.is_available() and next(model.parameters()).is_cuda:
                        gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024
                        L.info(f"  GPU memory allocated: {gpu_memory:.2f} MB")
                        
                else:
                    L.error(f"Model path {model_name} does not exist or is not a valid model directory")
                    return
                
                L.debug(f"EmbedModel init model:{model_name} cost time:{int((time.time()-start_time)*1000)}ms")
            except Exception as e:
                L.error(f"Failed to load embedding model {version} from {model_name}: {str(e)}")
    
    def _is_valid_model_path(self, model_path: str) -> bool:
        """检查路径是否包含有效的模型文件"""
        required_files = ['config.json']  # 最基本的配置文件
        optional_files = ['pytorch_model.bin', 'model.safetensors', 'config_sentence_transformers.json']
        
        # 检查必须文件
        for file in required_files:
            if not os.path.exists(os.path.join(model_path, file)):
                L.warning(f"Missing required file: {file} in {model_path}")
                return False
        
        # 检查是否至少有一个模型权重文件
        has_weights = any(os.path.exists(os.path.join(model_path, file)) for file in optional_files)
        if not has_weights:
            L.warning(f"No model weight files found in {model_path}")
            return False
            
        return True

    def _get_model(self, version) -> SentenceTransformer:
        # 如果请求的版本不可用，回退到默认版本
        if version not in EmbedModel.models:
            L.warning(f"Model version {version} not available, falling back to V2")
            version = EmbedModel.V2
        return EmbedModel.models[version]

    def embed(self, 
            query_texts: List[str], 
            normalize_embeddings=True, 
            version=None, 
            batch_size: int = 32,
            is_numpy=False):
        version = version if version is not None else self.default_version
        model = self._get_model(version)
        embeddings = model.encode(query_texts, 
                batch_size=batch_size,
                normalize_embeddings=normalize_embeddings)
        if is_numpy:
            return embeddings
        return embeddings.tolist()

    def embed_keyword_quantize(self, 
            query_texts: List[str], 
            normalize_embeddings=True, 
            version=None, 
            batch_size: int = 128,
            precision="int8",
            ranges: Optional[np.ndarray] = None):
        version = version if version is not None else self.default_version
        model = self._get_model(version)
        embeddings = model.encode(query_texts, 
                batch_size=batch_size,
                normalize_embeddings=normalize_embeddings)
        
        quant_embeddings = quantize_embeddings(
            embeddings,
            precision=precision,
            ranges=ranges,
        )
        return quant_embeddings.tolist()

    def score(self, query_text: str, target_texts: List[str], normalize_embeddings=True, version=None):
        version = version if version is not None else self.default_version
        if not target_texts:
            return []
        model = self._get_model(version)
        query_emb = model.encode([query_text], normalize_embeddings=normalize_embeddings)
        text_embs = model.encode(target_texts, normalize_embeddings=normalize_embeddings)
        similarity = query_emb @ text_embs.T
        return similarity[0]

    def score_list(self, query_texts: List[str], target_texts: List[str], normalize_embeddings=True, version=None):
        version = version if version is not None else self.default_version
        if not target_texts:
            return np.empty((len(query_texts), 0))
        model = self._get_model(version)
        query_embs = model.encode(query_texts, normalize_embeddings=normalize_embeddings)
        text_embs = model.encode(target_texts, normalize_embeddings=normalize_embeddings)
        similarity = query_embs @ text_embs.T
        return similarity
    
if __name__ == "__main__":
    scorer = EmbedModel()

    texts1 = ["胡子长得太快怎么办？"]
    texts2 = ["怎样使胡子不浓密！", "香港买手表哪里好", "在杭州手机到哪里买"]

    similarity = scorer.score(texts1[0], texts2)
    print(similarity)
