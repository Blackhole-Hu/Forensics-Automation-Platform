# CTF 电子取证平台 - 功能增强 PRD

## Problem Statement

作为 CTF 比赛选手，我以往在 Reasonix 桌面端通过 skill 进行电子取证，但存在以下痛点：

1. **可视化程度低** — 纯文本终端输出，难以快速理解取证进度
2. **证据难追溯** — 输出淹没在对话历史中，无法系统化查看
3. **证据链不完整** — 手动记录容易遗漏关键操作
4. **结果缺乏审查** — AI 输出直接使用，缺乏验证机制
5. **工具调用不集成** — 每次都需要手动告诉 AI 使用哪些工具
6. **难以完全自主** — 需要人工指导每一步，效率低下

## Solution

构建一个集成式电子取证平台，作为 Reasonix 的前端界面：

- **Reasonix 作为 AI agent 后端** — 负责理解题目、制定策略、调用工具
- **平台提供可视化界面** — 实时展示取证进度、资源浏览、证据链
- **自动化证据链记录** — 每个操作自动记录，确保可复现性
- **结果审查机制** — 标记关键发现，支持人工确认/修正

## User Stories

1. As a CTF 选手, I want to 输入检材路径和题目要求（自然语言），so that 平台能自动开始取证分析
2. As a CTF 选手, I want to 实时查看 Reasonix 的思考过程，so that 我能理解 AI 的决策逻辑
3. As a CTF 选手, I want to 实时查看工具执行进度，so that 我知道当前在做什么
4. As a CTF 选手, I want to 关键发现（flag、密码、IP）自动高亮，so that 我能快速识别重要信息
5. As a CTF 选手, I want to 浏览 Reasonix 解析出来的文件，so that 我能查看原始证据
6. As a CTF 选手, I want to 查看完整的证据链时间线，so that 我能复现取证过程
7. As a CTF 选手, I want to 标记和确认关键发现，so that 我能验证结果的正确性
8. As a CTF 选手, I want to 手动调用取证工具，so that 我能进行针对性分析
9. As a CTF 选手, I want to 生成取证报告，so that 我能提交比赛答案
10. As a CTF 选手, I want to 查看历史取证任务，so that 我能回顾之前的分析
11. As a CTF 选手, I want to 导出证据链为 JSON/CSV，so that 我能保存取证记录
12. As a CTF 选手, I want to Reasonix 自动选择合适的取证工具，so that 我不需要手动指定
13. As a CTF 选手, I want to 查看 Reasonix 的工具调用历史，so that 我能了解分析过程
14. As a CTF 选手, I want to 在取证过程中暂停和恢复，so that 我能灵活控制分析节奏
15. As a CTF 选手, I want to 对 Reasonix 的输出进行人工修正，so that 我能纠正 AI 的错误
16. As a CTF 选手, I want to 查看每个发现的来源（哪个工具、哪一步），so that 我能追溯线索
17. As a CTF 选手, I want to 平台自动记录所有操作到证据链，so that 我不需要手动记录
18. As a CTF 选手, I want to 查看取证过程的统计信息（耗时、工具调用次数），so that 我能评估效率
19. As a CTF 选手, I want to 支持多种证据类型（磁盘镜像、内存转储、APK、日志），so that 我能处理各类题目
20. As a CTF 选手, I want to 平台与本地取证工具集成（Volatility、Autopsy、JADX），so that 我能使用专业工具

## Implementation Decisions

### 1. 后端重构：AnalysisExecutor

**决策**：将 `_execute_analysis()` 巨型函数重构为独立的 `AnalysisExecutor` 服务类。

**接口设计**：
```python
class AnalysisExecutor:
    def __init__(self, db: AsyncSession, broadcast_fn: Callable):
        self.db = db
        self.broadcast = broadcast_fn
    
    async def execute(self, task_id: int, tool: str, file_path: str, params: dict):
        # 主入口
        pass
    
    async def _update_task_status(self, task_id: int, status: str, progress: float):
        pass
    
    async def _execute_tool(self, tool: str, file_path: str, params: dict) -> dict:
        pass
    
    async def _save_findings(self, task_id: int, findings: list):
        pass
    
    async def _check_evidence_completion(self, evidence_id: int):
        pass
```

**事务策略**：多个小事务
- 工具执行可能耗时很长，不适合放在大事务中
- 每个关键步骤（状态更新、保存发现、更新证据）独立事务

**依赖注入**：
- `db` — 数据库 session
- `broadcast_fn` — WebSocket 广播函数（解耦 WebSocket manager）

### 2. Reasonix CLI 集成

**决策**：通过 subprocess 调用 Reasonix CLI，流式获取输出。

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
        - type: thinking/tool/finding/error
        - content: 内容
        - metadata: 附加信息
        """
        pass
```

**调用方式**：
```bash
reasonix run "分析这个检材 {path}，题目要求：{question}"
```

**输出解析**：
- `💭` 或 `thinking` → AI 思考过程
- `⚡` 或 `tool` → 工具调用
- `⭐` 或 `finding` → 关键发现
- `📁` 或 `file` → 文件操作
- `❌` 或 `error` → 错误信息

### 3. 前端实时展示

**决策**：时间线 + 高亮展示，按时间顺序，关键信息突出显示。

**组件设计**：
- `ReasonixTimeline.vue` — 主时间线组件
- `TimelineItem.vue` — 单个时间项
- `FindingHighlight.vue` — 关键发现高亮

**WebSocket 消息格式**：
```json
{
    "type": "thinking|tool|finding|file|error|progress",
    "timestamp": "2026-07-08T14:23:01Z",
    "content": "需要先分析文件系统结构...",
    "metadata": {
        "tool": "volatility",
        "command": "volatility -f disk.img pslist",
        "finding_type": "flag",
        "severity": "critical"
    }
}
```

**样式**：
- `💭` 蓝色背景 — AI 思考
- `⚡` 灰色背景 — 工具执行
- `⭐` 黄色背景 — 关键发现（高亮）
- `📁` 绿色背景 — 文件操作
- `❌` 红色背景 — 错误

### 4. 资源浏览器

**决策**：查看 Reasonix 生成的文件，支持下载和预览。

**功能**：
- 文件树展示（目录结构）
- 文件内容预览（文本、图片、十六进制）
- 文件下载
- 文件搜索

**API**：
```
GET /api/files — 获取文件树
GET /api/files/{path} — 获取文件内容
GET /api/files/{path}/download — 下载文件
```

### 5. 证据链增强

**决策**：自动记录每个操作，支持导出。

**记录内容**：
- 操作类型（upload/analyze/finding/export）
- 操作时间
- 操作详情（JSON）
- 关联的证据和任务

**导出格式**：
- JSON — 完整数据
- CSV — 表格格式
- Markdown — 可读格式

### 6. 结果审查

**决策**：标记关键发现，支持人工确认/修正。

**审查状态**：
- `pending` — 待审查
- `confirmed` — 已确认
- `rejected` — 已拒绝
- `modified` — 已修正

**审查操作**：
- 确认发现
- 拒绝发现
- 修正发现内容
- 添加审查备注

## Testing Decisions

### 测试原则

1. **只测试外部行为**，不测试实现细节
2. **依赖注入** — mock 外部依赖（数据库、WebSocket、Reasonix CLI）
3. **每个 seam 独立测试** — AnalysisExecutor、ReasonixService、前端组件

### 测试模块

1. **AnalysisExecutor**
   - 测试 execute() 主流程
   - 测试 _update_task_status() 状态更新
   - 测试 _save_findings() 发现保存
   - 测试 _check_evidence_completion() 完成检查
   - Mock: db session, broadcast_fn

2. **ReasonixService**
   - 测试 analyze() 流式输出
   - 测试 parse_output() 输出解析
   - Mock: subprocess

3. **ReasonixRouter**
   - 测试 API 端点
   - 测试 WebSocket 推送
   - Mock: ReasonixService

4. **前端组件**
   - 测试时间线渲染
   - 测试 WebSocket 连接
   - Mock: API 调用

### 测试优先级

1. AnalysisExecutor（核心）
2. ReasonixService（关键集成）
3. 前端组件（用户体验）

## Out of Scope

1. **多用户支持** — 当前只支持单用户
2. **权限管理** — 无认证/授权
3. **分布式部署** — 单机部署
4. **AI 模型训练** — 使用现有模型
5. **移动端适配** — 只支持桌面端
6. **离线模式** — 需要网络连接

## Further Notes

### 依赖

- Python 3.12+
- FastAPI + SQLAlchemy
- Vue.js 3 + Pinia
- Reasonix CLI（已安装）
- 本地取证工具（Volatility、Autopsy、JADX 等）

### 配置

- `reasonix.toml` — Reasonix 配置
- `.env` — 环境变量（API keys）
- `config.py` — 平台配置

### 部署

```bash
# 后端
cd backend && python3 -m uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm run dev
```

### 优先级

1. **P0（必须）**
   - AnalysisExecutor 重构
   - Reasonix CLI 集成
   - 基础实时展示

2. **P1（重要）**
   - 资源浏览器
   - 证据链增强
   - 结果审查

3. **P2（可选）**
   - 高级统计
   - 报告生成增强
   - 多证据关联分析
