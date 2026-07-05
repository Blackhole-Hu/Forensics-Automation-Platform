# Triage Labels

Five canonical triage roles mapped to GitHub label strings:

| Role | Label String | Description |
|------|-------------|-------------|
| needs-triage | `needs-triage` | 维护者需要评估 |
| needs-info | `needs-info` | 等待报告人提供更多信息 |
| ready-for-agent | `ready-for-agent` | 规格完整，AI 代理可直接接手 |
| ready-for-human | `ready-for-human` | 需要人工实现 |
| wontfix | `wontfix` | 不处理 |

## Usage

When `/triage` processes an incoming issue, it applies these labels to move the issue through the state machine.
