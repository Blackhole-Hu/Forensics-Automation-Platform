"""
证据管理路由
"""
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Evidence, EvidenceStatus, Finding, EvidenceChain
from app.schemas import (
    EvidenceResponse, FindingResponse, EvidenceChainResponse
)
from app.services.evidence_service import EvidenceService

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.post("/upload", response_model=EvidenceResponse)
async def upload_evidence(
    file: UploadFile = File(...),
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """上传证据文件"""
    # 读取文件内容
    content = await file.read()
    file_size = len(content)

    # 保存文件
    file_path, unique_name = EvidenceService.save_upload(content, file.filename)

    # 计算哈希
    md5_hash, sha256_hash = EvidenceService.calculate_hashes(file_path)

    # 识别类型
    evidence_type = EvidenceService.detect_type(file_path, file.filename)

    # 创建数据库记录
    evidence = Evidence(
        filename=unique_name,
        original_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        evidence_type=evidence_type,
        status=EvidenceStatus.PENDING,
        md5=md5_hash,
        sha256=sha256_hash,
        description=description
    )

    db.add(evidence)
    await db.flush()
    await db.refresh(evidence)

    # 记录证据链
    chain = EvidenceChain(
        evidence_id=evidence.id,
        event_type="upload",
        description=f"上传文件: {file.filename} ({file_size} bytes)",
        details={"original_name": file.filename, "file_size": file_size}
    )
    db.add(chain)
    await db.commit()

    return evidence


@router.get("/", response_model=list[EvidenceResponse])
async def list_evidence(
    status: Optional[str] = None,
    evidence_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """列出所有证据"""
    query = select(Evidence)

    if status:
        query = query.where(Evidence.status == status)
    if evidence_type:
        query = query.where(Evidence.evidence_type == evidence_type)

    query = query.offset(skip).limit(limit).order_by(Evidence.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(evidence_id: int, db: AsyncSession = Depends(get_db)):
    """获取证据详情"""
    evidence = await db.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.get("/{evidence_id}/findings", response_model=list[FindingResponse])
async def get_findings(
    evidence_id: int,
    finding_type: Optional[str] = None,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取证据的所有发现"""
    query = select(Finding).where(Finding.evidence_id == evidence_id)

    if finding_type:
        query = query.where(Finding.finding_type == finding_type)
    if severity:
        query = query.where(Finding.severity == severity)

    query = query.order_by(Finding.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{evidence_id}/chain", response_model=list[EvidenceChainResponse])
async def get_evidence_chain(evidence_id: int, db: AsyncSession = Depends(get_db)):
    """获取证据链"""
    result = await db.execute(
        select(EvidenceChain)
        .where(EvidenceChain.evidence_id == evidence_id)
        .order_by(EvidenceChain.timestamp.desc())
    )
    return result.scalars().all()


@router.delete("/{evidence_id}")
async def delete_evidence(evidence_id: int, db: AsyncSession = Depends(get_db)):
    """删除证据"""
    evidence = await db.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    # 删除物理文件
    try:
        Path(evidence.file_path).unlink(missing_ok=True)
    except Exception:
        pass

    await db.delete(evidence)
    await db.commit()
    return {"message": "Evidence deleted"}
