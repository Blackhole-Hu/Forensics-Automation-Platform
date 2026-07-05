"""
电子取证平台 - FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import evidence, analysis, websocket


app = FastAPI(
    title="CTF 电子取证平台",
    description="集成式电子取证比赛工具平台",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(evidence.router)
app.include_router(analysis.router)
app.include_router(websocket.router)


# 静态文件服务
import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup():
    """启动时初始化数据库"""
    await init_db()


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "CTF Forensic Platform",
        "version": "1.0.0"
    }


@app.get("/api/dashboard")
async def dashboard():
    """仪表盘数据"""
    from sqlalchemy import select, func
    from app.database import async_session_factory
    from app.models import Evidence, AnalysisTask, Finding

    async with async_session_factory() as db:
        # 证据统计
        total_evidence = await db.execute(select(func.count(Evidence.id)))
        pending = await db.execute(
            select(func.count(Evidence.id)).where(Evidence.status == "pending")
        )
        analyzing = await db.execute(
            select(func.count(Evidence.id)).where(Evidence.status == "analyzing")
        )
        completed = await db.execute(
            select(func.count(Evidence.id)).where(Evidence.status == "completed")
        )

        # 发现统计
        total_findings = await db.execute(select(func.count(Finding.id)))
        critical = await db.execute(
            select(func.count(Finding.id)).where(Finding.severity == "critical")
        )

        # 任务统计
        total_tasks = await db.execute(select(func.count(AnalysisTask.id)))
        running_tasks = await db.execute(
            select(func.count(AnalysisTask.id)).where(AnalysisTask.status == "running")
        )

        return {
            "evidence": {
                "total": total_evidence.scalars().first() or 0,
                "pending": pending.scalars().first() or 0,
                "analyzing": analyzing.scalars().first() or 0,
                "completed": completed.scalars().first() or 0
            },
            "findings": {
                "total": total_findings.scalars().first() or 0,
                "critical": critical.scalars().first() or 0
            },
            "tasks": {
                "total": total_tasks.scalars().first() or 0,
                "running": running_tasks.scalars().first() or 0
            }
        }
