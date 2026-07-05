"""
分析引擎服务 - 调度取证工具执行分析
"""
import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime

from app.config import settings
from app.models import AnalysisTool


class AnalysisEngine:
    """
    分析引擎 - 负责调度各种取证工具
    """

    # 工具注册表
    _tools: dict[str, dict] = {}

    @classmethod
    def register_tool(cls, name: str, handler: Callable, description: str = ""):
        """注册一个分析工具"""
        cls._tools[name] = {
            "handler": handler,
            "description": description
        }

    @classmethod
    async def execute(
        cls,
        tool: str,
        file_path: str,
        params: Optional[dict] = None,
        progress_callback: Optional[Callable] = None
    ) -> dict:
        """
        执行分析任务
        """
        if tool not in cls._tools:
            return {
                "status": "error",
                "error": f"Unknown tool: {tool}"
            }

        handler = cls._tools[tool]["handler"]
        try:
            result = await handler(file_path, params or {}, progress_callback)
            return result
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    @classmethod
    def list_tools(cls) -> list[dict]:
        """列出所有可用工具"""
        return [
            {
                "name": name,
                "description": info["description"]
            }
            for name, info in cls._tools.items()
        ]


# ========== 工具实现 ==========


async def run_cli_tool(command: list[str], progress_callback=None) -> dict:
    """
    通用 CLI 工具执行器
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        output = stdout.decode('utf-8', errors='replace')
        error = stderr.decode('utf-8', errors='replace')

        return {
            "status": "completed" if proc.returncode == 0 else "error",
            "returncode": proc.returncode,
            "output": output,
            "error": error if proc.returncode != 0 else None
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "error": f"Command not found: {command[0]}"
        }


# Volatility3 内存分析
async def volatility_analysis(file_path: str, params: dict, progress_callback=None):
    config = params.get("config", {})
    profile = config.get("profile", "Win10")
    plugins = config.get("plugins", ["pslist", "netscan", "hivedump"])

    results = {}
    for plugin in plugins:
        cmd = [
            "python", "-m", "volatility3",
            "-f", file_path,
            f"--profile={profile}",
            plugin
        ]
        result = await run_cli_tool(cmd)
        results[plugin] = result

    return {
        "status": "completed",
        "output": json.dumps(results, ensure_ascii=False),
        "findings": _extract_volatility_findings(results)
    }


def _extract_volatility_findings(results: dict) -> list[dict]:
    """从 volatility 结果中提取关键发现"""
    findings = []

    for plugin, result in results.items():
        if result.get("status") != "completed":
            continue

        output = result.get("output", "")

        if plugin == "pslist":
            # 提取可疑进程
            for line in output.split('\n')[2:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        findings.append({
                            "type": "process",
                            "content": line.strip()
                        })

        elif plugin == "netscan":
            # 提取网络连接
            for line in output.split('\n')[2:]:
                if line.strip():
                    findings.append({
                        "type": "network_connection",
                        "content": line.strip()
                    })

    return findings


# JADX APK 反编译
async def jadx_analysis(file_path: str, params: dict, progress_callback=None):
    jadx_dir = Path(settings.tools_dir) / "jadx"
    jadx_bin = jadx_dir / "bin" / "jadx"

    output_dir = Path(settings.results_dir) / f"jadx_{Path(file_path).stem}"
    output_dir.mkdir(exist_ok=True)

    cmd = [
        str(jadx_bin),
        "-d", str(output_dir),
        file_path
    ]

    result = await run_cli_tool(cmd)

    return {
        "status": result["status"],
        "output": f"反编译输出目录: {output_dir}",
        "result_file": str(output_dir),
        "output_raw": result.get("output", "")
    }


# John the Ripper 密码破解
async def john_analysis(file_path: str, params: dict, progress_callback=None):
    john_dir = Path(settings.tools_dir) / "john" / "JtR"
    john_bin = john_dir / "run" / "john"

    wordlist = params.get("wordlist", str(john_dir / "passwords" / "password.lst"))

    cmd = [
        str(john_bin),
        "--wordlist=" + wordlist,
        file_path
    ]

    result = await run_cli_tool(cmd)

    return {
        "status": result["status"],
        "output": result.get("output", ""),
        "error": result.get("error")
    }


# StegSeek 隐写分析
async def stegseek_analysis(file_path: str, params: dict, progress_callback=None):
    stegseek_dir = Path(settings.tools_dir) / "stegseek"

    wordlist = params.get("wordlist", str(stegseek_dir / "dict.txt"))
    output_dir = params.get("output_dir", str(settings.results_dir))

    cmd = [
        str(stegseek_dir),
        "-d", wordlist,
        "-o", output_dir,
        file_path
    ]

    result = await run_cli_tool(cmd)

    return {
        "status": result["status"],
        "output": result.get("output", ""),
        "error": result.get("error")
    }


# PE 文件分析
async def pefile_analysis(file_path: str, params: dict, progress_callback=None):
    try:
        import pefile
        pe = pefile.PE(file_path)

        info = {
            "pe_type": "DLL" if pe.is_dll() else "EXE" if pe.is_exe() else "OTHER",
            "machine": pe.FILE_HEADER.Machine,
            "compile_time": str(pe.get_file_info()[0][0]['FileInfos'][0][0]['FixedFileInfo'][0]['FileTimestamp']) if pe.get_file_info() else "N/A",
            "imports": {},
            "sections": []
        }

        # 导入表
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                funcs = [f.decode() if isinstance(f, bytes) else f for f in entry.imports]
                info["imports"][entry.dll.decode()] = funcs

        # 节表
        for section in pe.sections:
            info["sections"].append({
                "name": section.Name.decode().rstrip('\x00'),
                "virtual_size": section.Misc_VirtualSize,
                "entropy": section.get_entropy()
            })

        pe.close()

        return {
            "status": "completed",
            "output": json.dumps(info, ensure_ascii=False, default=str)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# 自动关键词搜索
async def autogkat_analysis(file_path: str, params: dict, progress_callback=None):
    """通用文件内容搜索 - 搜索常见关键词"""
    keywords = params.get("keywords", [
        "password", "flag", "secret", "key", "token",
        "admin", "root", "passwd", "credential",
        "192.168", "10.0.", "172.16", "http://", "https://",
        "mysql://", "mongodb://", "redis://",
        "AKIA", "aws_secret", "PRIVATE KEY"
    ])

    findings = []
    try:
        with open(file_path, 'r', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                for kw in keywords:
                    if kw.lower() in line.lower():
                        findings.append({
                            "type": "keyword_match",
                            "line": i,
                            "keyword": kw,
                            "content": line.strip()[:200]
                        })
                if len(findings) >= 100:
                    break
    except Exception:
        pass

    return {
        "status": "completed",
        "output": json.dumps(findings[:50], ensure_ascii=False),
        "findings_count": len(findings)
    }


# 注册所有工具
AnalysisEngine.register_tool("volatility", volatility_analysis, "Volatility3 内存取证分析")
AnalysisEngine.register_tool("jadx", jadx_analysis, "JADX Android APK 反编译")
AnalysisEngine.register_tool("john", john_analysis, "John the Ripper 密码破解")
AnalysisEngine.register_tool("stegseek", stegseek_analysis, "StegSeek 隐写分析")
AnalysisEngine.register_tool("pefile", pefile_analysis, "PE 文件结构分析")
AnalysisEngine.register_tool("autogkat", autogkat_analysis, "自动关键词搜索")
