## Parent

#1 PRD: CTF 电子取证平台功能增强

## What to build

查看 Reasonix 生成的文件，支持下载和预览。

**核心改动**：
- 创建 `components/ResourceBrowser.vue` — 资源浏览器组件
- 创建 `routers/files.py` — 文件 API 端点
- 文件树展示（目录结构）
- 文件内容预览（文本、图片、十六进制）
- 文件下载

**API 端点**：
```
GET /api/files — 获取文件树
GET /api/files/{path} — 获取文件内容
GET /api/files/{path}/download — 下载文件
```

**功能**：
- 文件树展示（目录结构，可折叠）
- 文件内容预览：
  - 文本文件：语法高亮
  - 图片：缩略图预览
  - 二进制：十六进制视图
- 文件搜索
- 文件下载

**页面布局**：
- 左侧：文件树
- 右侧：文件内容预览

## Acceptance criteria

- [ ] `ResourceBrowser.vue` 组件已创建
- [ ] 文件树正确展示目录结构
- [ ] 文本文件预览正常
- [ ] 图片预览正常
- [ ] 文件下载正常

## Blocked by

- #3 集成 Reasonix CLI
