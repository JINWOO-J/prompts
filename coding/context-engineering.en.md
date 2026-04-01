---
category: coding
type: concept
tags:
- context-engineering
- prompt-engineering
- llm
role: Developer
origin: custom
source: 'https://www.pixelmojo.io/blogs/context-engineering-ai-coding-agents-beyond-claude-md'
---
# 컨텍스트 엔지니어링 — Context Engineering for AI Coding Agents

> Techniques for systematically providing the right context to AI coding agents to maximize output quality.

---

## Key Principles

- The model only knows what is in the current token stream — context is everything for the agent
- Specific commands are more powerful than general advice ("pnpm test" > "please run the tests")
- Examples are more effective than explanations — use code examples instead of rule descriptions
- Prohibitions are stronger than recommendations ("Do not use sed" > "Please use sd")
- Tables, lists, and code blocks are more effective than long prose
- CLAUDE.md is optimal at 200–500 lines — separate frequently changing information into dedicated files
- Use the @import pattern to link large documents by reference
- Maintain cross-session context with the 4-file working memory system (PRD, CLAUDE.md, planning.md, tasks.md)

## Details

After Andrej Karpathy proposed "vibe coding" in 2025, the industry shifted from "just accept AI suggestions" to a systematic approach called context engineering.

### The 4 Layers of Context

| Layer | Description | Example |
|-------|-------------|---------|
| System | Agent default behavior | System prompt |
| Project | Codebase rules | CLAUDE.md, AGENTS.md |
| Session | Current conversation | Chat history, file reads |
| Task | Current task | User prompt |

### Effective Context Strategies

1. **Specific commands > General advice**: "pnpm test" > "please run the tests"
2. **Examples > Explanations**: Code examples are more effective than rule descriptions
3. **Prohibitions > Recommendations**: "Do not use sed" is stronger than "Please use sd"
4. **Structure > Prose**: Tables, lists, and code blocks are more effective than long sentences

### Practical Patterns

**4-File Working Memory System**
```
PRD.md          — Product requirements
CLAUDE.md       — Project rules
planning.md     — Architecture decisions
tasks.md        — Task tracking
```

**@import Pattern**
Reference other files from CLAUDE.md:
```markdown
See @docs/architecture.md for system design
See @docs/api-spec.yaml for API contracts
```

**Token Budget Management**
- CLAUDE.md is optimal at 200–500 lines
- Separate frequently changing information into dedicated files
- Progressive disclosure via subdirectory-level CLAUDE.md files

## References

- [pixelmojo.io — Context Engineering for AI Coding Agents](https://www.pixelmojo.io/blogs/context-engineering-ai-coding-agents-beyond-claude-md)
