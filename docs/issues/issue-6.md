## Parent

#1 PRD: CTF 电子取证平台功能增强

## What to build

自动记录每个操作，支持导出为 JSON/CSV/Markdown。

**核心改动**：
- 增强 `EvidenceChain` 模型，添加更多字段
- 创建 `components/EvidenceChainTimeline.vue` — 证据链时间线
- 创建 `routers/chain.py` — 证据链 API 端点
- 支持导出为 JSON、CSV、Markdown

**记录内容**：
- 操作类型（upload/analyze/finding/export/review）
- 操作时间
- 操作详情（JSON）
- 关联的证据和任务
- 操作者（AI/人工）

**API 端点**：
```
GET /api/chain/{evidence_id} — 获取证据链
GET /api/chain/{evidence_id}/export/json — 导出 JSON
GET /api/chain/{evidence_id}/export/csv — 导出 CSV
GET /api/chain/{evidence_id}/export/markdown — 导出 Markdown
```

**页面布局**：
- 时间线展示（垂直）
- 筛选（按操作类型、时间范围）
- 导出按钮

## Acceptance criteria

- [ ] `EvidenceChainTimeline.vue` 组件已创建
- [ ] 证据链自动记录所有操作
- [ ] 时间线正确展示
- [ ] JSON 导出正常
- [ ] CSV 导出正常
- [ ] Markdown 导出正常

## Blocked by

- #2 重构 AnalysisExecutor
