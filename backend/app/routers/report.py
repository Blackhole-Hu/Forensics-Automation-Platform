"""
报告生成路由
"""
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Evidence, Finding, EvidenceChain, AnalysisTask
from app.services.ai_analyzer import ai_analyzer

router = APIRouter(prefix="/api/report", tags=["report"])


@router.post("/generate")
async def generate_report(
    evidence_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """生成取证分析报告"""
    # 获取证据
    evidence = await db.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    # 获取所有发现
    findings_result = await db.execute(
        select(Finding).where(Finding.evidence_id == evidence_id)
    )
    findings = findings_result.scalars().all()

    # 获取证据链
    chain_result = await db.execute(
        select(EvidenceChain).where(EvidenceChain.evidence_id == evidence_id)
        .order_by(EvidenceChain.timestamp.asc())
    )
    chain = chain_result.scalars().all()

    # 获取分析任务
    tasks_result = await db.execute(
        select(AnalysisTask).where(AnalysisTask.evidence_id == evidence_id)
    )
    tasks = tasks_result.scalars().all()

    # 构建摘要
    summary = {
        "evidence": {
            "filename": evidence.original_name,
            "type": evidence.evidence_type,
            "size": evidence.file_size,
            "md5": evidence.md5,
            "sha256": evidence.sha256
        },
        "analysis_tasks": [
            {
                "tool": t.tool,
                "status": t.status,
                "output": (t.output or "")[:500]
            }
            for t in tasks
        ],
        "findings": [
            {
                "type": f.finding_type,
                "severity": f.severity,
                "title": f.title,
                "content": f.content
            }
            for f in findings
        ],
        "evidence_chain": [
            {
                "event": c.event_type,
                "description": c.description,
                "timestamp": str(c.timestamp)
            }
            for c in chain
        ]
    }

    # 生成报告
    if ai_analyzer.api_key:
        report = await ai_analyzer.generate_report(summary)
    else:
        # 无 AI 时生成基础报告
        report = generate_basic_report(summary)

    return {
        "evidence_id": evidence_id,
        "report": report,
        "summary": summary
    }


def generate_basic_report(summary: dict) -> str:
    """生成基础报告（无 AI）"""
    ev = summary["evidence"]
    findings = summary["findings"]
    tasks = summary["analysis_tasks"]
    chain = summary["evidence_chain"]

    report = f"""# 电子取证分析报告

## 1. 证据信息

| 属性 | 值 |
|------|-----|
| 文件名 | {ev['filename']} |
| 类型 | {ev['type']} |
| 大小 | {ev['size']} bytes |
| MD5 | {ev['md5']} |
| SHA256 | {ev['sha256']} |

## 2. 分析过程

共执行 {len(tasks)} 个分析任务：

"""
    for t in tasks:
        report += f"- **{t['tool']}**: {t['status']}\n"

    report += f"""
## 3. 发现

共发现 {len(findings)} 条线索：

"""
    for f in findings:
        report += f"- [{f['severity'].upper()}] **{f['title']}**: {f['content']}\n"

    report += f"""
## 4. 证据链

| 时间 | 事件 | 描述 |
|------|------|------|
"""
    for c in chain:
        report += f"| {c['timestamp']} | {c['event']} | {c['description']} |\n"

    report += """
## 5. 结论

根据以上分析，已提取所有关键线索。

---
*本报告由 CTF 电子取证平台自动生成*
"""

    return report
