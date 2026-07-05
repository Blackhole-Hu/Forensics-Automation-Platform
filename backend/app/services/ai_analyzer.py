"""
AI 分析服务 - 使用大模型进行智能取证分析
"""
import json
from typing import Optional, List
from app.config import settings


class AIAnalyzer:
    """AI 驱动的取证分析器"""

    def __init__(self):
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model

    async def analyze_evidence(
        self,
        evidence_type: str,
        content: str,
        context: Optional[str] = None,
        question: Optional[str] = None
    ) -> dict:
        """
        对证据内容进行 AI 分析
        """
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)

        system_prompt = self._build_system_prompt(evidence_type, context)
        user_prompt = self._build_user_prompt(content, question)

        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4096
            )

            content = response.choices[0].message.content
            return self._parse_ai_response(content)

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "raw_output": ""
            }

    async def analyze_tool_output(
        self,
        tool_name: str,
        tool_output: str,
        question: Optional[str] = None
    ) -> dict:
        """
        对工具输出结果进行 AI 分析，提取关键发现
        """
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)

        system_prompt = f"""你是一个专业的电子取证分析师。
你的任务是分析 {tool_name} 工具的输出结果，提取有价值的线索。

请以 JSON 格式返回分析结果：
{{
    "summary": "简要总结",
    "findings": [
        {{
            "type": "发现类型 (ip/password/flag/file/process/network/etc)",
            "severity": "info/warning/critical",
            "title": "发现标题",
            "content": "具体内容",
            "explanation": "为什么这个发现重要"
        }}
    ],
    "suggestions": ["后续分析建议"]
}}"""

        user_prompt = f"""工具: {tool_name}
问题: {question or '请分析以下输出，提取有价值的线索'}

工具输出:
```
{tool_output[:8000]}
```

请分析并返回 JSON 结果："""

        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4096
            )

            content = response.choices[0].message.content
            return self._parse_json_response(content)

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def generate_report(self, evidence_summary: dict) -> str:
        """
        生成取证分析报告
        """
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)

        system_prompt = """你是一个专业的电子取证报告撰写者。
根据提供的证据和发现，撰写一份专业的取证分析报告。

报告格式：
1. 概述 - 简要说明取证目标和范围
2. 证据清单 - 列出所有分析的证据
3. 分析过程 - 描述使用的工具和方法
4. 发现 - 详细列出所有重要发现
5. 结论 - 总结主要结论
6. 建议 - 后续行动建议

请使用专业的取证术语，报告要清晰、客观、可追溯。"""

        user_prompt = f"""请根据以下信息生成取证分析报告：

{json.dumps(evidence_summary, ensure_ascii=False, indent=2)}"""

        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=8192
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"报告生成失败: {str(e)}"

    def _build_system_prompt(self, evidence_type: str, context: Optional[str]) -> str:
        """构建系统提示词"""
        base = f"""你是一个专业的电子取证分析师，正在进行 CTF 比赛中的电子取证任务。

当前分析的证据类型: {evidence_type}
"""
        if context:
            base += f"\n背景信息: {context}\n"

        base += """
你的任务是：
1. 识别证据中的关键信息
2. 提取可能的线索（IP、密码、flag、文件路径等）
3. 分析异常行为
4. 提供后续分析建议

请以 JSON 格式返回：
{
    "summary": "分析摘要",
    "findings": [...],
    "suggestions": [...]
}"""

        return base

    def _build_user_prompt(self, content: str, question: Optional[str]) -> str:
        """构建用户提示词"""
        prompt = f"请分析以下证据内容：\n\n```{content[:8000]}```"
        if question:
            prompt += f"\n\n具体问题: {question}"
        return prompt

    def _parse_ai_response(self, content: str) -> dict:
        """解析 AI 响应"""
        try:
            # 尝试提取 JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content

            data = json.loads(json_str)
            return {
                "status": "completed",
                "data": data
            }
        except (json.JSONDecodeError, IndexError):
            return {
                "status": "completed",
                "raw_output": content
            }

    def _parse_json_response(self, content: str) -> dict:
        """解析 JSON 格式的 AI 响应"""
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content

            data = json.loads(json_str)
            return {
                "status": "completed",
                "data": data
            }
        except (json.JSONDecodeError, IndexError):
            return {
                "status": "completed",
                "raw_output": content
            }


# 全局实例
ai_analyzer = AIAnalyzer()
