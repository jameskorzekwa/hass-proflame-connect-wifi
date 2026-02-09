# Agent Protocols

These instructions are intended for the AI agent to follow when working in this repository.

## Info

the url for my home assistant instance is https://home.jklocal.us

## On Code Changes

Whenever you modify any code in this repository, you MUST perform the following checks to ensure code quality and correctness:

1.  **Linting**: Run the linting script to check for style and potential errors.
    ```bash
    ./scripts/lint
    ```
    This script uses `ruff` to check and automatically fix some issues.

2.  **Unit Tests**:
    *   Run the unit tests using `pytest`:
    ```bash
    poetry run pytest
    ```
    *   **Action for Agent**: Ensure all new logic is covered by unit tests. If you modify existing logic, ensure existing tests pass.

3.  **Dependencies**:
    *   If you add new imports, ensure `pyproject.toml` is updated.
    *   Run `poetry install` or `poetry update` if `pyproject.toml` changes.

## Commit Message Conventions (Required for Releases)

This repository uses **semantic-release** with the `@semantic-release/commit-analyzer` plugin. A new GitHub Release (and version tag) is **only** created when the commit message follows the [Conventional Commits](https://www.conventionalcommits.org/) format:

| Prefix | Release Type | Example Version Change |
|---|---|---|
| `fix: ...` or `fix(scope): ...` | Patch | `1.0.4` → `1.0.5` |
| `feat: ...` or `feat(scope): ...` | Minor | `1.0.4` → `1.1.0` |
| `BREAKING CHANGE: ...` in the footer | Major | `1.0.4` → `2.0.0` |

**If the commit message does not start with `fix:` or `feat:` (or similar recognized prefixes), no release will be created.**

### Examples

```
# ✅ WILL trigger a release
fix(config_flow): prevent duplicate device discovery
feat: add support for multiple fireplaces

# ❌ Will NOT trigger a release
Add connectivity check during DHCP discovery
Update tests for config flow
Refactor client module
```

## General Guidelines

-   Follow semantic versioning principles.
-   Keep the `README.md` and `info.md` updated if functionality changes significantly.
-   Use `run_command` to execute the scripts rather than assuming their output.

## Post-Push Workflow Checks

After pushing code changes to the repository, you MUST:

1.  **Monitor Workflows**: Use the `github-mcp-server` to list recent workflow runs for the branch you pushed to.
    *   Tool: `github-mcp-server_actions_list` (method: `list_workflow_runs`)
    *   Wait for the runs associated with your commit SHA to complete.

2.  **Verify Success**: Ensure all workflows (Lint, Release, Validate, etc.) have a status of `completed` and conclusion of `success`.

3.  **Handle Failures**:
    *   If a workflow fails, investigate the failure using the logs if possible.
    *   Propose and implement fixes for the issue.
    *   Repeat the local checks (linting, testing) before pushing the fix.
