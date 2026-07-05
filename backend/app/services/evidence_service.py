"""
证据管理服务 - 文件上传、类型识别、哈希计算
"""
import hashlib
import os
from pathlib import Path
from typing import Optional
from app.config import settings


class EvidenceService:
    """证据文件管理服务"""

    # MIME 类型映射表（基于文件扩展名）
    EXT_TO_MIME = {
        '.dd': 'application/octet-stream',
        '.img': 'application/octet-stream',
        '.dmg': 'application/x-apple-diskimage',
        '.vmdk': 'application/x-vmdk',
        '.vhdx': 'application/x-vhdx',
        '.vhd': 'application/x-vhd',
        '.qcow2': 'application/x-qcow2',
        '.raw': 'application/octet-stream',
        '.e01': 'application/octet-stream',
        '.mem': 'application/octet-stream',
        '.dmp': 'application/octet-stream',
        '.pcap': 'application/vnd.tcpdump.pcap',
        '.pcapng': 'application/vnd.tcpdump.pcap',
        '.cap': 'application/vnd.tcpdump.pcap',
        '.apk': 'application/vnd.android.package-archive',
        '.exe': 'application/x-dosexec',
        '.dll': 'application/x-dosexec',
        '.sys': 'application/x-dosexec',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.bmp': 'image/bmp',
        '.gif': 'image/gif',
        '.tiff': 'image/tiff',
        '.webp': 'image/webp',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.txt': 'text/plain',
        '.log': 'text/plain',
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.zip': 'application/zip',
        '.rar': 'application/x-rar-compressed',
        '.7z': 'application/x-7z-compressed',
    }

    @staticmethod
    def detect_type(file_path: str, filename: str) -> str:
        """
        自动识别证据类型
        """
        ext = Path(filename).suffix.lower()
        basename = Path(filename).stem.lower()

        # 磁盘镜像
        disk_exts = {'.dd', '.img', '.dmg', '.vmdk', '.vhdx', '.vhd', '.qcow2', '.e01'}
        if ext in disk_exts or 'disk' in basename or '镜像' in basename:
            return "disk_image"

        # 内存转储
        memory_exts = {'.mem', '.dmp', '.lm'}
        if ext in memory_exts or 'memory' in basename or 'memdump' in basename:
            return "memory_dump"

        # 网络抓包
        network_exts = {'.pcap', '.pcapng', '.cap', '.sng'}
        if ext in network_exts or 'pcap' in basename:
            return "network_capture"

        # Android APK
        if ext == '.apk' or ext == '.apkx':
            return "android_apk"

        # 日志文件
        log_exts = {'.log', '.syslog', '.audit'}
        if ext in log_exts or 'log' in basename:
            return "log_file"

        # 图片（可能含隐写）
        image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        if ext in image_exts:
            return "image"

        # PE 文件
        if ext in {'.exe', '.dll', '.sys', '.drv'}:
            return "binary"

        # 文档
        doc_exts = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.odt'}
        if ext in doc_exts:
            return "document"

        return "other"

    @staticmethod
    def calculate_hashes(file_path: str) -> tuple[str, str]:
        """计算 MD5 和 SHA256"""
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                md5.update(chunk)
                sha256.update(chunk)

        return md5.hexdigest(), sha256.hexdigest()

    @staticmethod
    def save_upload(file_bytes: bytes, filename: str) -> tuple[str, str]:
        """
        保存上传文件，返回 (保存路径, 唯一文件名)
        """
        import uuid
        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"
        save_path = settings.upload_dir / unique_name

        with open(save_path, 'wb') as f:
            f.write(file_bytes)

        return str(save_path), unique_name

    @staticmethod
    def get_file_size(file_path: str) -> int:
        return os.path.getsize(file_path)


def mime_type(file_path: str) -> str:
    """获取文件 MIME 类型（基于扩展名）"""
    ext = Path(file_path).suffix.lower()
    # 使用 EvidenceService 的映射表
    from app.services.evidence_service import EvidenceService
    return EvidenceService.EXT_TO_MIME.get(ext, "application/octet-stream")
