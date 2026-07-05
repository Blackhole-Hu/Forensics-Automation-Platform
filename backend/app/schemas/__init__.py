"""
Pydantic Schemas - 请求/响应模型
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models import EvidenceStatus, EvidenceType


# ========== 证据相关 ==========

class EvidenceCreate(BaseModel):
    """上传证据请求"""
    filename: str
    original_name: str
    file_size: int
    mime_type: Optional[str] = None
    description: Optional[str] = None


class EvidenceResponse(BaseModel):
    """证据响应"""
    id: int
    filename: str
    original_name: str
    file_size: int
    mime_type: Optional[str]
    evidence_type: str
    status: str
    md5: Optional[str]
    sha256: Optional[str]
    created_at: datetime
    description: Optional[str]

    class Config:
        from_attributes = True


# ========== 分析任务相关 ==========

class AnalysisTaskCreate(BaseModel):
    """创建分析任务"""
    evidence_id: int
    tool: str
    params: Optional[dict] = None


class AnalysisTaskResponse(BaseModel):
    """分析任务响应"""
    id: int
    evidence_id: int
    tool: str
    status: str
    progress: float
    command: Optional[str]
    output: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ========== 发现相关 ==========

class FindingResponse(BaseModel):
    """发现响应"""
    id: int
    evidence_id: int
    finding_type: str
    severity: str
    title: Optional[str]
    content: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 证据链相关 ==========

class EvidenceChainResponse(BaseModel):
    """证据链响应"""
    id: int
    evidence_id: int
    event_type: str
    description: str
    timestamp: datetime

    class Config:
        from_attributes = True


# ========== WebSocket 消息 ==========

class WSProgress(BaseModel):
    """进度推送"""
    task_id: int
    progress: float
    message: str


class WSResult(BaseModel):
    """结果推送"""
    task_id: int
    finding_type: str
    severity: str
    title: str
    content: str
