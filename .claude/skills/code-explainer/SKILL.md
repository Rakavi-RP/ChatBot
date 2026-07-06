---
name: code-explainer
description: Explain unfamiliar codebases in a structured way to help developers understand the flow and architecture before making changes. Use when the user asks to understand, walk through, or get onboarded to a codebase or specific files, e.g. "explain this codebase", "how does this app work", "walk me through this file", "what happens when this runs".
---

# Code Explainer

## Purpose

Explain unfamiliar codebases in a structured way so a developer understands the flow and architecture before making changes.

## Workflow

1. **Identify the application entry point.** Find where execution begins (main function, entry script, server bootstrap, index file, etc.).
2. **Explain the execution exactly as the runtime/interpreter executes it** — not the order files appear in the directory tree.
3. **Give a high-level overview of the architecture** before diving into details.
4. **Explain the responsibility of each file and folder** relevant to the task.
5. **Walk through the execution path step by step**, following the real control flow (imports, calls, callbacks, event handlers) from entry point onward.
6. **For requested files, explain functions/classes in execution order**, not the order they appear in the file.
7. **Explain why each component exists and how it interacts with others** — the role it plays in the system, not just what it does.
8. **Highlight important design patterns, dependencies, and data flow** where they aid understanding.
9. **Mention edge cases or implementation details only if they help understanding** — do not exhaustively list every branch or corner case.

## Constraints

- Do not suggest refactoring, improvements, or fixes unless the user explicitly asks for them. This skill is for explanation only.
- Favor clarity and correct ordering (runtime order) over completeness. It's fine to skip unrelated files/branches that don't aid understanding of the requested flow.
