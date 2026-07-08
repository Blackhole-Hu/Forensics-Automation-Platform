## Parent

#1 PRD: CTF 电子取证平台功能增强

## What to build

标记关键发现，支持人工确认/修正。

**核心改动**：
- 增强 `Finding` 模型，添加审查状态和备注
- 创建 `components/FindingReview.vue` — 发现审查组件
- 创建 `routers/review.py` — 审查 API 端点
- 审查操作：确认、拒绝、修正、添加备注

**审查状态**：
- `pending` — 待审查
- `confirmed` — 已确认
- `rejected` — 已拒绝
- `modified` — 已修正

**API 端点**：
```
GET /api/findings/{finding_id} — 获取发现详情
PUT /api/findings/{finding_id}/review — 审查发现
- status: confirmed|rejected|modified
- notes: string (可选)
- content: string (修正内容，status=modified 时)
```

**页面布局**：
- 发现列表（按严重程度排序）
- 审查操作按钮
- 审查历史

## Acceptance criteria

- [ ] `FindingReview.vue` 组件已创建
- [ ] 审查状态正确更新
- [ ] 审查历史正确记录
- [ ] 修正内容正确保存

## Blocked by

- #4 前端实时展示增强
