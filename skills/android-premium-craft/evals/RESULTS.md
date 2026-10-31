# Eval results

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
