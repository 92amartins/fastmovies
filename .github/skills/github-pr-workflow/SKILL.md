---
name: github-pr-workflow
description: 'Use when taking a repository change from implementation to a GitHub pull request. Guides branch creation, concrete-anchor investigation, minimal edits, focused validation, review, commit, push, and PR creation.'
argument-hint: 'Describe the change, issue or acceptance criteria, and target base branch.'
user-invocable: true
---

# GitHub Pull Request Workflow

Use this skill when the user wants a complete, reviewable GitHub pull request. Confirm the target repository, base branch, and change scope. Treat implementation and local review as authorized by the request, but require a final confirmation immediately before committing, pushing, or opening the PR.

## 1. Inspect Before Acting

Inspect the repository state and remote before changing anything:

- current branch and working-tree status
- configured remote and its repository identity
- recent branch names and the target base branch
- relevant project instructions, tests, and contribution guidance

Never discard or overwrite existing user changes. If the working tree contains unrelated edits, preserve them and either work around them or ask before proceeding when they prevent a clean branch or commit.

## 2. Create a Working Branch

Use the target base branch as the starting point and create a new descriptive branch before editing. Choose a repository-compatible name such as `fix/<short-description>`, `feat/<short-description>`, or `chore/<short-description>`.

Do not use a branch that already contains unrelated work. If the current state cannot be branched cleanly, explain the blocker instead of stashing, resetting, or deleting changes without explicit approval.

## 3. Establish and Implement the Change

Start from the most concrete anchor: a named file, symbol, endpoint, failing behavior, test, or acceptance criterion. Read only enough nearby code to identify the code that directly controls the behavior and one cheap check that could disconfirm the assumption.

State a falsifiable local hypothesis before editing. If the starting file only wires or forwards behavior, follow one hop to the nearest decision point. Then make the smallest change that tests the hypothesis.

- Preserve public APIs, local conventions, and unrelated user changes.
- Prefer existing helpers and patterns over new abstractions.
- Keep comments rare and only explain non-obvious reasoning.
- Add or adjust focused tests when behavior or a contract changes.

After the first substantive edit, run the narrowest executable check available before more reading or patching:

1. the failing or behavior-scoped check
2. a focused test for the touched slice
3. a narrow compile, lint, or type check
4. diff inspection if no executable check is available

Keep validation aligned with the edit. For this repository, prefer focused `pytest` tests first, then the broader project checks documented in `README.md` and `.github/copilot-instructions.md`.

## 4. Review the Proposed Change

Interpret validation locally: repair and rerun the same check when it supports the hypothesis; take one nearby hop and revise the hypothesis when it disproves it; inspect one nearby dependency when it is ambiguous. Do not fix unrelated failures.

Before committing, review the complete diff and status for:

- correctness, security, error handling, and backward compatibility
- tests covering changed behavior and meaningful edge cases
- accidental files, generated artifacts, secrets, debug output, or unrelated edits
- documentation and public contract updates where needed

Use the repository's review or test commands when available. Resolve findings and rerun focused validation after every substantive review fix.

## 5. Confirm, Commit, and Push

After validation and review pass, summarize the intended commit, branch, remote, and PR target and ask for confirmation before any externally visible GitHub action. Do not commit, push, or open a PR until that confirmation is received.

After confirmation, stage specific intended files, inspect the staged diff, and create one clear imperative commit unless the repository's contribution guidance says otherwise. Do not amend or rewrite existing commits without explicit approval.

Push the new branch to the configured remote with upstream tracking. Never force-push by default. If authentication, permissions, or remote configuration blocks the push, report the exact blocker and leave the local commit intact.

## 6. Open the Pull Request

Create the PR against the confirmed base branch using the available VS Code/GitHub integration first, with `gh pr create` as a fallback. The title should state the user-visible change. The body should include:

- summary of the change
- implementation or behavior details that help reviewers
- tests and validation commands run
- known limitations, unrelated failures, or follow-up work

Link the issue or acceptance criteria when provided. Return the PR URL and the final branch and commit identifiers. If PR creation is unavailable, provide the pushed branch and a ready-to-use title and body instead.

## Decision Rules

| Situation | Action |
|-----------|--------|
| Existing user changes are present | Preserve them; ask only if they block safe delivery |
| Base branch or remote is unclear | Inspect local configuration and ask before branching or publishing |
| Behavior owner is clear | Edit it and run its narrow check |
| First check fails locally | Repair the same slice and rerun it |
| Review finds a defect | Fix it, validate again, and re-review the diff |
| Failure is unrelated | Leave it unchanged and report it |
| Push or PR creation is blocked | Keep the local commit and report the actionable blocker |
| Commit, push, or PR confirmation is not granted | Stop before that action and report the completed local work |

## Completion Checklist

- [ ] Change is on a new branch from the intended base
- [ ] Relevant tests and focused validation pass
- [ ] Full diff and staged diff were reviewed
- [ ] No secrets, unrelated edits, or generated artifacts were committed
- [ ] Commit message describes the change
- [ ] Branch is pushed without force
- [ ] PR targets the intended base and includes summary, tests, and risks
- [ ] User received the PR URL or the exact publication blocker
