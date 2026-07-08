"""
分析任务路由
"""
import json
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Evidence, AnalysisTask, Finding, EvidenceChain, EvidenceStatus
from app.schemas import AnalysisTaskResponse
from app.services.analysis_engine import AnalysisEngine
from app.routers.websocket import manager

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/run", response_model=AnalysisTaskResponse)
async def run_analysis(
    evidence_id: int = Form(...),
    tool: str = Form(...),
    params: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """启动分析任务"""
    # 解析 params JSON
    parsed_params = {}
    if params:
        try:
            parsed_params = json.loads(params)
        except json.JSONDecodeError:
            parsed_params = {}

    # 验证证据存在
    evidence = await db.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    # 更新证据状态
    evidence.status = EvidenceStatus.ANALYZING
    await db.flush()

    # 创建分析任务
    task = AnalysisTask(
        evidence_id=evidence_id,
        tool=tool,
        status="pending",
        command=params,
        progress=0.0
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)

    # 记录证据链
    chain = EvidenceChain(
        evidence_id=evidence_id,
        event_type="analyze_start",
        description=f"开始分析: {tool}",
        details=json.dumps({"tool": tool, "task_id": task.id, "params": parsed_params}, ensure_ascii=False)
    )
    db.add(chain)
    await db.commit()

    # 异步执行分析
    if background_tasks:
        background_tasks.add_task(
            _execute_analysis,
            task.id,
            tool,
            evidence.file_path,
            parsed_params
        )

    return task


@router.get("/tools")
async def list_tools():
    """列出可用工具"""
    return AnalysisEngine.list_tools()


@router.get("/{evidence_id}", response_model=list[AnalysisTaskResponse])
async def get_tasks(evidence_id: int, db: AsyncSession = Depends(get_db)):
    """获取证据的分析任务列表"""
    result = await db.execute(
        select(AnalysisTask)
        .where(AnalysisTask.evidence_id == evidence_id)
        .order_by(AnalysisTask.created_at.desc())
    )
    return result.scalars().all()


@router.get("/task/{task_id}", response_model=AnalysisTaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """获取分析任务详情"""
    task = await db.get(AnalysisTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def _execute_analysis(task_id: int, tool: str, file_path: str, params: dict):
    """执行分析任务的后台任务"""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from app.config import settings

    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        try:
            # 更新状态为运行中
            task = await db.get(AnalysisTask, task_id)
            if not task:
                return

            task.status = "running"
            task.progress = 10.0
            await db.commit()
            
            # 广播进度
            await manager.broadcast(task.evidence_id, {
                "type": "progress",
                "task_id": task_id,
                "progress": 10.0,
                "message": f"开始 {tool} 分析..."
            })

            # 创建进度回调函数
            async def progress_callback(progress: float, message: str = ""):
                task = await db.get(AnalysisTask, task_id)
                if task:
                    task.progress = progress
                    await db.commit()
                    # WebSocket 广播
                    await manager.broadcast(task.evidence_id, {
                        "type": "progress",
                        "task_id": task_id,
                        "progress": progress,
                        "message": message
                    })

            # 执行分析
            result = await AnalysisEngine.execute(
                tool,
                file_path,
                params,
                progress_callback
            )

            # 更新任务结果
            task = await db.get(AnalysisTask, task_id)
            task.status = result.get("status", "error")
            task.progress = 100.0
            task.output = result.get("output", "")

            if result.get("error"):
                task.error_message = result["error"]

            await db.commit()
            
            # 广播完成
            await manager.broadcast(task.evidence_id, {
                "type": "task_complete",
                "task_id": task_id,
                "status": task.status,
                "message": f"{tool} 分析完成"
            })

            # 处理发现
            findings = result.get("findings", [])
            if findings:
                for finding in findings:
                    f = Finding(
                        evidence_id=task.evidence_id,
                        task_id=task.id,
                        finding_type=finding.get("type", "unknown"),
                        severity=finding.get("severity", "info"),
                        title=finding.get("title", f"{tool} 发现"),
                        content=finding.get("content", ""),
                        raw_data=str(finding)
                    )
                    db.add(f)

                    # 记录证据链
                    chain = EvidenceChain(
                        evidence_id=task.evidence_id,
                        event_type="finding",
                        description=f"发现: {finding.get('type', 'unknown')} - {finding.get('title', '')}",
                        details=json.dumps(finding, ensure_ascii=False, default=str)
                    )
                    db.add(chain)
                    
                    # 广播发现
                    await manager.broadcast(task.evidence_id, {
                        "type": "finding",
                        "task_id": task_id,
                        "finding": {
                            "type": finding.get("type", "unknown"),
                            "severity": finding.get("severity", "info"),
                            "title": finding.get("title", ""),
                            "content": finding.get("content", "")[:200]
                        }
                    })

                await db.commit()

            # 更新证据状态
            evidence = await db.get(Evidence, task.evidence_id)
            if evidence:
                # 检查是否还有其他运行中的任务
                active_tasks = await db.execute(
                    select(AnalysisTask).where(
                        AnalysisTask.evidence_id == task.evidence_id,
                        AnalysisTask.status.in_(["pending", "running"])
                    )
                )
                if not active_tasks.scalars().all():
                    evidence.status = EvidenceStatus.COMPLETED
                    
                    # 广播证据分析完成
                    await manager.broadcast(task.evidence_id, {
                        "type": "evidence_complete",
                        "evidence_id": task.evidence_id,
                        "message": "所有分析任务已完成"
                    })

                await db.commit()

        except Exception as e:
            task = await db.get(AnalysisTask, task_id)
            if task:
                task.status = "error"
                task.error_message = str(e)
                await db.commit()
                
                await manager.broadcast(task.evidence_id, {
                    "type": "error",
                    "task_id": task_id,
                    "message": f"分析失败: {str(e)}"
                })

            evidence = await db.get(Evidence, task.evidence_id) if task else None
            if evidence:
                evidence.status = EvidenceStatus.ERROR
                await db.commit()
