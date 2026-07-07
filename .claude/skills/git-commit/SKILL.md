---
name: git-commit
description: Review and safely commit Git changes with a step-by-step confirmation gate before every command. Use when the user asks to commit, review changes before committing, or wants a guided commit/push flow, e.g. "commit my changes", "help me commit", "review and commit", "/git-commit".
---

# Git Commit

## Purpose

Guide the user through reviewing and committing Git changes safely, stopping for explicit confirmation before running each command. Nothing gets staged, committed, or pushed without the user saying yes at that specific step.

## Hard rule

**Stop after every step below and wait for the user's explicit confirmation before running the next command.** Never chain multiple git commands together without a confirmation in between. If the user says no, or asks to stop, stop — do not run the remaining steps.

## Workflow

1. **Ask for confirmation to begin.** Confirm the user wants to start the review/commit flow before running anything.

2. **Run `git status`.** Explain the output in plain terms: which files are modified, newly added (staged), deleted, or untracked. Group them clearly (e.g. "Modified: ...", "Untracked: ...", "Deleted: ...").

3. **Run `git diff`** to inspect unstaged tracked changes.

If untracked files exist:
- Inform the user that `git diff` will not display untracked files.
- Summarize the untracked files by explaining what they contain and their purpose.
- If the user wants more detail, display or explain the contents of those files.
- Continue with the workflow.

4. **Ask whether to stage the changes.** Wait for a yes/no answer.

5. **If confirmed, run `git add .`.** Do not run this without step 4's confirmation. After running, briefly confirm what got staged (e.g. via `git status` if helpful).

6. **Ask the user for a commit message.** Do not invent one yourself unless the user explicitly asks you to draft one — if they ask you to draft it, propose it and get their explicit approval on the wording before using it.

7. **Run `git commit -m "<commit-message>"`** using the confirmed message.

8. **After the commit succeeds:**
   - Run `git log -1 --stat`.
   - Show:
     - The commit hash.
     - The commit message.
     - The files included in the commit.
   - Briefly explain what was committed.

9. **Ask whether the user wants to push the commit.** Wait for a yes/no answer.

10. **If they choose to push:**
    - Determine the current branch (e.g. `git branch --show-current`) and tell the user which branch is checked out.
    - Ask for explicit confirmation to push to that specific branch. Never assume `main` or any other branch.
    - Push to the current branch only, e.g. `git push origin <current-branch>`.

11. **At every step, stop and wait for the user's confirmation before executing the next command.**

## Constraints

- Never use destructive or history-rewriting flags (`--force`, `--amend`, `--hard`, etc.) as part of this flow.
- Never skip git hooks (`--no-verify`) unless the user explicitly asks for it.
- Never push to a branch other than the currently checked-out one without explicit instruction.
- If `git status` or `git diff` show nothing to commit, tell the user and stop rather than proceeding through the remaining steps.
