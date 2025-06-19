from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from aivc.config.config import settings, L
from aivc.api import ws
from aivc.api import router
import uvicorn
import os
import asyncio
from aivc.model.embed.embed import EmbedModel
from aivc.common.file import cleanup_old_files
from contextlib import asynccontextmanager

# 全局变量存储模型实例
embed_model = None
cleanup_task = None

async def periodic_cleanup():
    """定期清理任务"""
    while True:
        try:
            await asyncio.sleep(12 * 3600)  # 等待12小时
            L.info("开始执行定期文件清理任务")
            result = await cleanup_old_files()
            L.info(f"定期清理任务完成: {result}")
        except Exception as e:
            L.error(f"定期清理任务出错: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    global embed_model, cleanup_task
    
    L.info("Starting application...")
    
    # 创建必要的目录
    directories = ["ui", "docs", "upload"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            L.debug(f"Created directory: {directory}")
    
    # 挂载静态文件
    app.mount("/ui", StaticFiles(directory="ui"), name="ui")
    app.mount("/doc", StaticFiles(directory="docs"), name="docs")
    app.mount("/upload", StaticFiles(directory="upload"), name="upload")
    
    # 初始化模型
    try:
        L.info("Initializing models...")
        embed_model = EmbedModel()
            
        L.info("Models initialized successfully")
    except Exception as e:
        L.error(f"Failed to initialize models: {str(e)}")
        raise
    
    # 启动定期清理任务
    try:
        L.info("启动定期文件清理任务（每12小时执行一次）")
        cleanup_task = asyncio.create_task(periodic_cleanup())
        
        # 立即执行一次清理
        L.info("执行初始文件清理")
        initial_result = await cleanup_old_files()
        L.info(f"初始清理完成: {initial_result}")
        
    except Exception as e:
        L.error(f"启动清理任务失败: {e}")
    
    yield  # 应用运行期间
    
    # 关闭时执行
    L.info("Shutting down application...")
    
    # 取消定期清理任务
    if cleanup_task and not cleanup_task.done():
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            L.info("定期清理任务已取消")
    
    # 清理模型资源
    try:
        # EmbedModel 通常不需要特殊清理，但可以添加日志
        if embed_model:
            L.info("Embed model resources released")
            
    except Exception as e:
        L.error(f"Error during model cleanup: {str(e)}")
    
    L.info("Application shutdown complete")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return FileResponse("ui/index.html")

@app.get("/trace")
def read_trace():
    return FileResponse("ui/trace.html")

app.include_router(ws.router, tags=["ws"])
app.include_router(router.api_router_v1, prefix=settings.API_V1_STR, tags=["api_v1"])


if __name__ == "__main__":
    L.debug(f"API Listen {settings.LISTEN_IP}:{settings.PORT}")
    uvicorn.run(app, host=settings.LISTEN_IP, port=settings.PORT)