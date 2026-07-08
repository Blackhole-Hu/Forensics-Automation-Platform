## Parent

#1 PRD: CTF 电子取证平台功能增强

## What to build

通过 CLI 调用 Reasonix，实现流式输出，支持自然语言输入。

**核心改动**：
- 创建 `services/reasonix_service.py`，封装 Reasonix CLI 调用
- 创建 `routers/reasonix.py`，提供 API 端点
- 流式输出解析：提取思考、工具调用、发现、文件操作、错误

**ReasonixService 接口**：
```python
class ReasonixService:
    async def analyze(self, path: str, question: str) -> AsyncGenerator[str, None]:
        """
        流式调用 Reasonix CLI
        - path: 检材路径
        - question: 题目要求（自然语言）
        - yields: Reasonix 的输出行
        """
        pass
    
    def parse_output(self, line: str) -> dict:
        """
        解析 Reasonix 输出，提取关键信息
        - type: thinking|tool|finding|file|error
        - content: 内容
        - metadata: 附加信息
        """
        pass
```

**API 端点**：
```
POST /api/reasonix/analyze
- 路径: string
- 问题: string
- 返回: WebSocket 连接 URL
```

**调用方式**：
```bash
reasonix run "分析这个检材 {path}，题目要求：{question}"
```

## Acceptance criteria

- [ ] `ReasonixService` 已创建并通过单元测试
- [ ] `/api/reasonix/analyze` 端点正常工作
- [ ] 流式输出正确解析为 5 种类型
- [ ] WebSocket 实时推送 Reasonix 输出

## Blocked by

- #2 重构 AnalysisExecutor
