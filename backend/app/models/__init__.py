"""
电子取证平台 - SQLAlchemy 模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import enum


class Base(DeclarativeBase):
    pass


class EvidenceStatus(str, enum.Enum):
    """证据状态"""
    PENDING = "pending"           # 等待分析
    ANALYZING = "analyzing"       # 分析中
    COMPLETED = "completed"       # 分析完成
    ERROR = "error"               # 分析出错


class EvidenceType(str, enum.Enum):
    """证据类型"""
    DISK_IMAGE = "disk_image"       # 磁盘镜像
    MEMORY_DUMP = "memory_dump"     # 内存转储
    NETWORK_CAPTURE = "network_capture"  # 网络抓包
    LOG_FILE = "log_file"           # 日志文件
    ANDROID_APK = "android_apk"     # Android APK
    PCAP = "pcap"                   # PCAP 文件
    DOCUMENT = "document"           # 文档
    IMAGE = "image"                 # 图片（含隐写）
    BINARY = "binary"               # 二进制文件
    OTHER = "other"                 # 其他


class AnalysisTool(str, enum.Enum):
    """取化工具"""
    VOLATILITY = "volatility"       # 内存分析
    YARA = "yara"                   # 恶意代码扫描
    JADX = "jadx"                   # APK 反编译
    JOHN = "john"                   # 密码破解
    STEGSEEK = "stegseek"           # 隐写分析
    PEFILE = "pefile"               # PE 文件分析
    AUTOGKAT = "autogkat"           # 自动关键词搜索
    AI_ANALYSIS = "ai_analysis"     # AI 分析


class Evidence(Base):
    """证据文件"""
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100))
    evidence_type = Column(String(50), default=EvidenceType.OTHER)
    status = Column(String(20), default=EvidenceStatus.PENDING)
    md5 = Column(String(32))
    sha256 = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = Column(Text)

    # 关系
    analysis_tasks = relationship("AnalysisTask", back_populates="evidence", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="evidence", cascade="all, delete-orphan")
    evidence_chain = relationship("EvidenceChain", back_populates="evidence", cascade="all, delete-orphan")


class AnalysisTask(Base):
    """分析任务"""
    __tablename__ = "analysis_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=False)
    tool = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, error
    progress = Column(Float, default=0.0)
    command = Column(Text)  # 执行的命令
    output = Column(Text)   # 工具输出
    result_file = Column(String(500))  # 结果文件路径
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # 关系
    evidence = relationship("Evidence", back_populates="analysis_tasks")


class Finding(Base):
    """发现/线索"""
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("analysis_tasks.id"))
    finding_type = Column(String(50), nullable=False)  # ip, password, flag, file, process, etc.
    severity = Column(String(20), default="info")  # info, warning, critical
    title = Column(String(255))
    content = Column(Text)
    raw_data = Column(Text)  # 原始数据
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    evidence = relationship("Evidence", back_populates="findings")


class EvidenceChain(Base):
    """证据链"""
    __tablename__ = "evidence_chain"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # upload, analyze, find, export, etc.
    description = Column(Text)
    details = Column(Text)  # JSON 格式的详细数据
    timestamp = Column(DateTime, default=datetime.utcnow)

    # 关系
    evidence = relationship("Evidence", back_populates="evidence_chain")
