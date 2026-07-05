# 电子取证平台 - 领域上下文

## 项目概述

CTF 电子取证平台是一个集成式自动化取证工具，专为 CTF 比赛和电子取证场景设计。平台整合了本地取证工具、AI 大模型分析和实时反馈机制，提供从证据上传到报告生成的一站式工作流。

## 领域术语表

| 术语 | 英文 | 说明 |
|------|------|------|
| 证据 | Evidence | 上传到平台进行分析的文件，如磁盘镜像、内存转储、APK、日志等 |
| 分析任务 | Analysis Task | 对证据执行的单次分析操作，对应一个具体的取证工具 |
| 发现 | Finding | 分析过程中提取的关键线索，如 IP 地址、密码、flag、进程信息等 |
| 证据链 | Evidence Chain | 记录证据从上传到分析全过程的时间线，保证可追溯性 |
| 取证工具 | Forensic Tool | 用于分析的 CLI 工具，如 Volatility、JADX、John the Ripper、StegSeek |
| 内存取证 | Memory Forensics | 从内存转储文件中提取进程、网络连接、注册表等信息 |
| APK 反编译 | APK Decompilation | 将 Android APK 反编译为 Java 源码进行分析 |
| 隐写分析 | Steganography Analysis | 检测图片等文件中隐藏的加密容器或秘密信息 |
| 密码破解 | Password Cracking | 对密码哈希进行字典/暴力破解 |
| PE 分析 | PE Analysis | 分析 Windows PE 文件结构、导入表、节表等信息 |

## 证据类型

```
EvidenceType
├── disk_image       # 磁盘镜像 (.dd, .img, .vmdk, .vhdx, .e01)
├── memory_dump      # 内存转储 (.raw, .mem, .dmp)
├── network_capture  # 网络抓包 (.pcap, .pcapng)
├── log_file         # 日志文件 (.log, .syslog)
├── android_apk      # Android APK (.apk)
├── binary           # 二进制文件 (.exe, .dll)
├── image            # 图片文件 (.jpg, .png, .bmp)
├── document         # 文档文件 (.pdf, .doc, .xlsx)
└── other            # 其他类型
```

## 分析流程

```
用户上传证据 → 自动类型识别 → 计算哈希 → 选择分析工具 → 执行分析 → 提取发现 → 更新证据链 → 生成报告
```

### 详细流程

1. **上传阶段**
   - 接收文件，保存到 `uploads/` 目录
   - 自动识别文件类型（基于扩展名 + MIME 类型）
   - 计算 MD5/SHA256 哈希值
   - 记录证据链事件：`upload`

2. **分析阶段**
   - 用户选择工具，创建分析任务
   - 更新证据状态为 `analyzing`
   - 异步执行工具分析
   - 通过 WebSocket 实时推送进度
   - 记录证据链事件：`analyze_start`

3. **发现阶段**
   - 从工具输出中提取关键发现
   - 可选 AI 分析，智能识别线索
   - 记录证据链事件：`finding`

4. **完成阶段**
   - 所有任务完成后更新证据状态为 `completed`
   - 可生成分析报告

## 技术架构

### 后端 (Python FastAPI)

```
backend/
├── app/
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── main.py            # FastAPI 应用入口
│   ├── models/            # SQLAlchemy ORM 模型
│   ├── schemas/           # Pydantic 请求/响应模型
│   ├── routers/           # API 路由
│   │   ├── evidence.py    # 证据管理 API
│   │   ├── analysis.py    # 分析任务 API
│   │   └── websocket.py   # WebSocket 实时推送
│   ├── services/          # 业务逻辑
│   │   ├── evidence_service.py   # 证据管理服务
│   │   ├── analysis_engine.py    # 分析引擎（调度工具）
│   │   └── ai_analyzer.py        # AI 分析器
│   └── tools/             # 工具适配器
├── uploads/               # 上传文件存储
├── results/               # 分析结果存储
└── forensic.db            # SQLite 数据库
```

### 前端 (Vue.js 3)

```
frontend/
├── src/
│   ├── App.vue            # 主布局（侧边栏 + 内容区）
│   ├── main.js            # Vue 入口
│   ├── router/            # Vue Router 路由
│   ├── stores/            # Pinia 状态管理
│   │   └── evidence.js    # 证据状态
│   ├── services/          # API 服务
│   │   └── api.js         # Axios + WebSocket
│   ├── views/             # 页面组件
│   │   ├── Dashboard.vue  # 仪表盘
│   │   ├── EvidenceList.vue # 证据管理
│   │   ├── Analysis.vue   # 分析任务
│   │   ├── Findings.vue   # 发现列表
│   │   └── Report.vue     # 报告生成
│   └── styles/            # 全局样式
└── vite.config.js         # Vite 构建配置
```

## 本地工具集成

平台通过 `subprocess` 调用本地取证工具，工具路径配置在 `E:\CompetitionTools\tools`：

| 工具 | 路径 | 用途 |
|------|------|------|
| JADX | `tools/jadx/` | Android APK 反编译 |
| John the Ripper | `tools/john/JtR/` | 密码哈希破解 |
| StegSeek | `tools/stegseek/` | 图片隐写分析 |

## 数据库模型

```
Evidence (证据)
├── id, filename, original_name, file_path
├── file_size, mime_type, evidence_type
├── status (pending/analyzing/completed/error)
├── md5, sha256
└── → AnalysisTask (一对多)
   └── → Finding (多对多)

EvidenceChain (证据链)
├── event_type (upload/analyze_start/finding/export)
├── description, details (JSON)
└── timestamp
```

## 关键设计决策

1. **异步分析** — 使用 FastAPI BackgroundTasks 执行长时间分析任务，避免阻塞 API
2. **WebSocket 实时推送** — 分析进度和发现通过 WebSocket 实时推送到前端
3. **工具注册表模式** — 分析引擎使用注册表模式，方便扩展新工具
4. **证据链记录** — 每个操作都记录到证据链，保证取证过程可追溯
5. **AI 辅助分析** — 可选 AI 分析层，对工具输出进行智能解读

## 扩展点

- **新工具集成** — 在 `analysis_engine.py` 中添加 handler 并注册
- **新证据类型** — 在 `EvidenceType` 枚举中添加，在 `detect_type()` 中补充识别逻辑
- **新 AI 模型** — 修改 `ai_analyzer.py` 中的 model 配置
- **新前端页面** — 在 `views/` 添加组件，在 `router/` 添加路由
