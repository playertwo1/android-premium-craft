# Eval results

## Contents
- v2.3.3, with and without, blinded review
- v2.3.2, trigger check with the snippet
- v2.3.1, trigger check only
- v2.3.0, first with-and-without run

## 2026-11-01, skill v2.3.3, claude-sonnet-5-5, with and without, blinded review

Runner: `evals/run_evals.py`. 9 scenarios x 2 arms x 3 runs = 54 runs, each in its own workspace with an opaque id. The "with" arm has the skill plus `assets/AGENTS_SNIPPET.md` as `CLAUDE.md`; the "without" arm has neither. The "Deliberately sloppy" line was removed from the copied `HomeScreen.kt`. Scored by claude-opus-5-5, which saw only the final reply, tool calls and files written, with paths and skill loading removed. No tool call was blocked.

| Scenario | Skill loaded | With | Without |
|---|---:|---:|---:|
| critique-sloppy-home | 3/3 | 19/24 | 1/24 |
| shape-finance-dashboard | 3/3 | 14/15 | 5/15 |
| build-settings-screen | 3/3 | 11/15 | 6/15 |
| less-generic | 3/3 | 9/12 | 7/12 |
| no-fake-fps | 3/3 | 6/12 | 6/12 |
| release-review-no-device | 3/3 | 9/9 | 1/9 |
| adapt-tablet | 3/3 | 13/15 | 3/15 |
| accessibility-audit | 3/3 | 5/12 | 0/12 |
| negative-backend (should not load) | 0/3 | 3/3 | 3/3 |
| **Total** | 24/24 | **89/117** | **32/117** |

Excluding the 8 criteria that name the skill's own artifacts (`SKILL_SPECIFIC` in the runner, chosen by the author of this round): 68/93 with, 31/93 without. Cost of the round: about US$6.

### Path to v2.3.3

- **v2.3.2 unchanged, first attempt:** 61/117 vs 33/117. Not usable: the model used the PowerShell tool, which the allowlist blocked, so `ui_audit.py`, `critique_score.py` and `review_gate.py` often did not run, and the output path contained the project name. Runner fixed.
- **v2.3.2 unchanged, second attempt:** 70/117 vs 38/117, 61/93 vs 36/93 excluding skill artifacts.
- **Changes to `SKILL.md`, one at a time, measured on the with-arm of the affected scenario only (3 runs each):**

| Change | Before | After | Kept |
|---|---:|---:|---|
| release-review: always write the evidence JSON, run the gate, list steps to `verified_for_scope` | 0/9 | 9/9 | yes |
| accessibility: split code from manual findings, name Compose fixes, end with the manual script | 3/12 | 8/12 | yes |
| accessibility: also require numbered steps and dp text sizes | 8/12 | 6/12 | no, reverted |
| performance: baseline plan before the first edit, suspects as hypotheses | 6/12 | 8/12 | yes |
| performance: stronger wording | 8/12 | 8/12 | no gain; stopped |
| adapt: SDK 36 and 37 consequences, name the `adaptive` skill | 9/15 | 14/15 | yes (in two steps: 11/15, then 14/15) |
| build: stress previews (dark, 200% font, RTL) | 9/15 | 12/15 | yes |
| critique: each issue states its mode | 17/24 | 15/24 | no, reverted |

### What is left

- **no-fake-fps:** no gain over the baseline (6/12 and 6/12 in the final round). The agent still edits code before proposing a baseline; two attempts did not change that.
- **accessibility-audit:** 5/12. The manual TalkBack and 200% text script is still not written out in steps, and the dp text size and `minimumInteractiveComponentSize()` are often missed. Two attempts, no stable gain.
- **critique-sloppy-home:** the review-before-lint order cannot be shown from tool order, and the action plan after the answers needs a second turn, so those two criteria are not reachable in one turn.
- **build-settings-screen:** the screen is never rendered because the workspace has no app module.

### Limits

- One model, three runs per cell. A difference of one or two criteria is noise: the same critique change moved 17/24 to 15/24 without any real effect.
- The per-scenario changes were measured only on their own scenario; the final round is the only check of side effects.
- Blinding is partial. The reviewer saw no paths or arm names, but replies that cite the Craft Score or the Method line reveal the skill. 8 criteria depend on those artifacts.
- The reviewer is an LLM and was not checked against a human score.
- Allowed shell commands were limited to a list (python, ls, cat, grep, find and a few more); runs are not otherwise sandboxed.
- The final round was interrupted once by a usage limit and resumed; the runner re-ran only the unfinished runs.
- Claude Code only. The module review (see CHANGELOG) was not measured.

## 2026-10-31, skill v2.3.2, claude-sonnet-5-5, trigger check with the snippet

Same setup as the v2.3.1 check below, plus `assets/AGENTS_SNIPPET.md` as the workspace's `CLAUDE.md`. Three runs per scenario. No criteria were scored.

| Setup | Skill loaded (8 scenarios) | False triggers (negative-backend) |
|---|---:|---:|
| Skill installed only (v2.3.1) | 13/24 | 0/3 |
| Skill plus snippet | **24/24** | 0/3 |

Limits: one model, Claude Code only, small fixture workspaces. Loading the skill does not prove better output; v2.3.2 output was not scored.

## 2026-10-31, skill v2.3.1, claude-sonnet-5-5, trigger check only

Three runs per scenario, with the skill installed. No criteria were scored in this round, so v2.3.1 has no met count.

| Scenario | Skill loaded |
|---|---:|
| adapt-tablet | 3/3 |
| less-generic | 3/3 |
| release-review-no-device | 3/3 |
| critique-sloppy-home | 2/3 |
| build-settings-screen | 1/3 |
| shape-finance-dashboard | 1/3 |
| accessibility-audit | 0/3 |
| no-fake-fps | 0/3 |
| **Total expected to load** | **13/24** |
| negative-backend (should not load) | 0/3 |

- Automatic triggering remains the main weakness. v2.3.0 loaded on 5 of 8 in a single pass, so this shows no proven gain.
- When the skill did not load on build-settings-screen, both runs built nothing and asked for `DESIGN.md`. The run that loaded it built the screen and listed its assumptions, but did not compile or render it.
- no-fake-fps gave no invented FPS figure in any of the 3 runs, without the skill.

## 2026-10-31, skill v2.3.0, claude-sonnet-5-5

One run per arm, 18 in total, in single non-interactive turns. Each run had its own workspace, with user skills and MCP servers off. Scored by a separate agent that did not write the skill.

| Scenario | Skill loaded | With | Without |
|---|---|---:|---:|
| critique-sloppy-home | yes | 6/8 | 0/8 |
| adapt-tablet | yes | 4/5 | 1/5 |
| less-generic | yes | 3/4 | 1/4 |
| release-review-no-device | yes | 1/3 | 1/3 |
| build-settings-screen | yes | 0/5 | 2/5 |
| shape-finance-dashboard | **no** | 3/5 | 2/5 |
| no-fake-fps | **no** | 2/4 | 2/4 |
| accessibility-audit | **no** | 1/4 | 1/4 |
| negative-backend | no (correct) | 1/1 | 1/1 |
| **Total** | 5 of 8 expected | **21/39** | **11/39** |

Excluding the 8 criteria that need the skill's own artifacts: 17/31 with, 10/31 without. In the 5 runs that loaded the skill: 14/25 with, 5/25 without.

### Failures

- **Trigger:** the skill did not load on 3 of 8 scenarios it covers, so those runs behaved like the baseline.
- **build-settings-screen:** with the skill, the agent built nothing and asked for direction, because only a DESIGN template was supplied. Without it, the agent built a screen and disclosed its assumptions, but never compiled or rendered it.
- **critique-sloppy-home:** lint ran before the written review, against the skill's order, and some file:line citations were off by one.
- **less-generic:** all caps was not named among the slop patterns.

### Limits

- One model and one run per arm: differences in a single scenario can be noise.
- Blinding was partial: run folder names and skill paths in the transcripts let the scorer often tell the arms apart.
- The scorer saw truncated action logs and final replies, not the written files or tool output.
- release-review-no-device: `review_gate.py` did not run because the test harness's command allowlist blocked it, so that score understates the skill.
- `evals/` was removed from the installed copy for these runs, because `install_skill.py` ships `evals.json`, the answer key.
- Criteria that span a later turn were scored only for the part achievable in one turn.
