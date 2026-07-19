# Appendix A -- Toy Concepts to Real Primitives

This course used standard-library toy implementations throughout, keeping
everything transparent and dependency-free. When you do loop engineering with
real tools (Claude Code, Codex, GitHub Actions, the MCP ecosystem), each
concept maps to an existing primitive. This table helps you connect what you
learned to the real world.

| Course toy | Real primitive | Notes |
|---|---|---|
| `mock_agent` / `noisy_agent` (Ch. 1, 8) | **One agent CLI run / LLM API call** | One run of Claude Code / Codex = one `act` in your loop. The inner ReAct loop it runs internally (Ch. 1, inner vs. outer). |
| `verify` / `run_check` (Ch. 2) | **Test / linter / CI / build exit code** | `pytest`, `ruff`, `npm run build`, health-check endpoint. Use deterministic checks whenever you can; reserve LLM judge for what you cannot write a rule for (Ch. 4). |
| Four safety guards (Ch. 3) | **Budget caps / structured logging / privilege tiers** | The real `loop-cost` (estimate spend) and `loop-audit` (assess health) automate these. |
| maker / checker (Ch. 4) | **Sub-agents** | One agent produces; another with a different system prompt verifies independently. Claude Code subagents, multi-agent orchestration. |
| `git worktree` isolation (Ch. 5) | **git worktree / containers / sandboxes** | Parallel loops each get an independent checkout; also prevents the agent from touching files it should not (injection mitigation). |
| `--once` + cron (Ch. 6) | **cron / systemd timer / GitHub Actions / scheduled cloud agents** | The scheduling layer is handled by these; your loop only needs to support "run one tick and exit." |
| External state JSON (Ch. 6) | **DB / issue queue / message queue / repo file** | Persistent state outside the process, so a scheduled loop can resume, deduplicate, and survive crashes. |
| durable spec (Ch. 9) | **`PLAN.md` / tests / issues in the repo; skills** | Write cross-round memory into the repo, not into conversation history. Claude Code skills are also a form of persistent knowledge. |
| Connecting to external systems (not covered) | **MCP (Model Context Protocol) connectors** | The standard protocol for letting agents access databases, APIs, and cloud services safely; real loops use it to obtain context and execute actions. |
| Loop-level evals (Ch. 10) | **Eval harness / loop-audit / observability dashboard** | Measure success rate / iters / escalation / cost across a task suite; A/B configurations before deploying. |

## One-liner

This course taught **the skeleton and discipline of the outer orchestration loop**.
The real world just swaps each part for a stronger primitive (agent CLI, MCP,
worktree, Actions, eval harness). **The skeleton does not change -- which is
exactly why learning the skeleton first is the most valuable investment.**

-> Back to [README](../README.md)
