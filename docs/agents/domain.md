# Domain Docs

## Layout

Multi-context layout.

The root `CONTEXT-MAP.md` lists all sub-projects and their context file locations.

## Structure

```
根目录/
├── CONTEXT-MAP.md          # 子项目目录索引
├── docs/adr/               # 跨项目共享的架构决策记录
├── [子项目A]/
│   ├── CONTEXT.md          # 子项目A的领域语言与上下文
│   └── docs/adr/           # 子项目A专属的架构决策
├── [子项目B]/
│   ├── CONTEXT.md          # 子项目B的领域语言与上下文
│   └── docs/adr/           # 子项目B专属的架构决策
└── ...
```

## Consumer Rules

1. Skills read the root `CONTEXT-MAP.md` first to discover available contexts.
2. When working on a specific sub-project, read that sub-project's `CONTEXT.md`.
3. Cross-project architectural decisions go in `docs/adr/`.
4. Sub-project-specific decisions go in the sub-project's `docs/adr/`.
