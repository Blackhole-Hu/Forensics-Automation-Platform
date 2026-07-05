# 🔍 CTF 电子取证平台

集成式自动化电子取证平台，专为 CTF 比赛和电子取证场景设计。整合本地取证工具、AI 大模型分析与实时反馈机制，提供从证据上传到报告生成的一站式工作流。

## ✨ 核心功能

- **证据管理** — 上传、分类、存储各类证据文件（磁盘镜像、内存转储、APK、日志、图片等）
- **自动识别** — 自动检测文件类型、计算哈希值
- **分析引擎** — 调度多种取证工具（Volatility、JADX、John the Ripper、StegSeek、PE 分析等）
- **AI 辅助** — 大模型智能分析工具输出，提取关键线索
- **实时反馈** — WebSocket 实时推送分析进度和发现
- **证据链** — 完整记录取证过程，保证可追溯性
- **报告生成** — 自动汇总分析结果生成取证报告

## 🏗️ 技术架构

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12+ / FastAPI / SQLAlchemy / WebSocket |
| 前端 | Vue.js 3 / Pinia / Vue Router / Vite |
| 数据库 | SQLite (可切换 PostgreSQL) |
| AI | OpenAI API (可切换其他大模型) |

## 📁 项目结构

```
电子取证项目/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── main.py            # FastAPI 入口
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API 路由
│   │   ├── services/          # 业务逻辑
│   │   │   ├── evidence_service.py   # 证据管理
│   │   │   ├── analysis_engine.py    # 分析引擎
│   │   │   └── ai_analyzer.py        # AI 分析
│   │   └── tools/             # 工具适配器
│   ├── uploads/               # 上传文件
│   ├── results/               # 分析结果
│   └── requirements.txt       # Python 依赖
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── App.vue            # 主布局
│   │   ├── main.js            # Vue 入口
│   │   ├── router/            # 路由
│   │   ├── stores/            # 状态管理
│   │   ├── services/          # API 服务
│   │   ├── views/             # 页面组件
│   │   └── styles/            # 全局样式
│   └── package.json           # Node.js 依赖
├── CONTEXT.md                  # 领域上下文文档
├── CONTEXT-MAP.md             # 多项目索引
├── AGENTS.md                  # AI 代理配置
└── docs/
    ├── agents/                # 代理配置文档
    └── adr/                   # 架构决策记录
```

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- npm

### 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 配置

1. 复制 `backend/.env.example` 为 `backend/.env`
2. 设置 `FORENSIC_AI_API_KEY`（可选，用于 AI 分析）
3. 修改 `backend/app/config.py` 中的工具路径

## 🔧 集成工具

平台默认集成以下工具：

| 工具 | 路径 | 功能 |
|------|------|------|
| JADX | `E:\CompetitionTools\tools\jadx` | Android APK 反编译 |
| John the Ripper | `E:\CompetitionTools\tools\john` | 密码破解 |
| StegSeek | `E:\CompetitionTools\tools\stegseek` | 隐写分析 |
| Volatility3 | `pip install volatility3` | 内存取证 |
| PEFile | `pip install pefile` | PE 文件分析 |

## 📡 API 文档

启动后端后访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

## 🔌 WebSocket 接口

- `/ws/{evidence_id}` — 监听特定证据的实时更新
- `/ws/all` — 监听所有证据的更新

消息格式：
```json
{
  "type": "progress" | "finding" | "complete" | "error",
  "task_id": 1,
  "progress": 50.0,
  "message": "分析中...",
  "data": {}
}
```

## 📝 扩展指南

### 添加新的取证工具

1. 在 `backend/app/services/analysis_engine.py` 中编写分析函数
2. 调用 `AnalysisEngine.register_tool(name, handler, description)` 注册

```python
async def my_tool_analysis(file_path: str, params: dict, progress_callback=None):
    # 你的分析逻辑
    return {"status": "completed", "output": "...", "findings": [...]}

AnalysisEngine.register_tool("my_tool", my_tool_analysis, "我的工具描述")
```

### 添加新的证据类型

1. 在 `EvidenceType` 枚举中添加新类型
2. 在 `EvidenceService.detect_type()` 中补充识别逻辑

## 📄 许可证

MIT License
