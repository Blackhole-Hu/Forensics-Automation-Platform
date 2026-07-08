## Parent

#1 PRD: CTF 电子取证平台功能增强

## What to build

时间线 + 高亮展示 Reasonix 的输出，按时间顺序，关键信息突出显示。

**核心改动**：
- 创建 `components/ReasonixTimeline.vue` — 主时间线组件
- 创建 `components/TimelineItem.vue` — 单个时间项
- 创建 `components/FindingHighlight.vue` — 关键发现高亮
- WebSocket 连接管理，实时接收 Reasonix 输出

**时间线样式**：
- 💭 蓝色背景 — AI 思考
- ⚡ 灰色背景 — 工具执行
- ⭐ 黄色背景 — 关键发现（高亮）
- 📁 绿色背景 — 文件操作
- ❌ 红色背景 — 错误

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

**页面布局**：
- 顶部：输入框（自然语言输入检材路径和题目要求）
- 中间：时间线（实时滚动）
- 右侧：发现列表（关键信息高亮）

## Acceptance criteria

- [ ] `ReasonixTimeline.vue` 组件已创建
- [ ] WebSocket 连接正常，实时接收消息
- [ ] 5 种类型的消息正确渲染
- [ ] 关键发现（flag、密码、IP）自动高亮
- [ ] 时间线自动滚动到最新消息

## Blocked by

- #3 集成 Reasonix CLI
