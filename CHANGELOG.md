# Changelog

## v2.3.2 - 2026-10-31

- Pasting `AGENTS_SNIPPET.md` into the app's `CLAUDE.md` raised skill loading from 13 of 24 runs to 24 of 24, with no false trigger in 3 negative runs (`evals/RESULTS.md`). The docs now say so.
- The snippet no longer says to lint before the review, and says what to do when `DESIGN.md` is missing.
- `ui_audit.py lint` says when it checked nothing, and `--fail-on` fails in that case.
- Corrected stale module, line and rule counts.

## v2.3.1 - 2026-10-31

Fixes from the first with-and-without eval run (`evals/RESULTS.md`).
- Shorter description with the triggers first. Automatic triggering is still unreliable: 13 of 24 runs, with no proven gain over v2.3.0. Name the skill for reliable use.
- `validate_skill.py` rejects a description that contains `: `, which is invalid YAML.
- `build` no longer stops when the direction or `DESIGN.md` is missing: it builds and lists its assumptions.
- `critique` repeats that the review comes before lint, and cited lines must be re-opened before reporting.
- `install_skill.py` no longer copies `evals/` and `tests/` into projects.

## v2.3.0 - 2026-10-31

Merged [Impeccable Mobile Studio](https://github.com/playertwo1/Impeccable-Mobile-Studio) (MIT) after running both projects on an emulator.
- New `scripts/mobile.py`: `capture`, `inspect`, `compare`, `test` (local Maestro with `--serial`), `preview`, `guidelines`, `doctor`. Evidence is never overwritten by default. Capture, inspect and compare need Pillow (`requirements.txt`); everything else stays stdlib.
- New `data/`: Compose, Flutter, React Native and cross-stack guideline tables from UI/UX Pro Max (MIT).
- New `modules/05-components/control-and-data-states.md`; before/after procedure in `visual-feedback-loop.md`; Flutter, React Native and Wear notes.
- `install_skill.py --replace` now verifies a staged copy, keeps the previous install under `.craft/install-backups`, restores it on failure, and refuses targets that leave the project through a link.
- Lint C004 also catches `color = Color.White.copy(alpha = ...)`. Found by the smoke test; scrim backgrounds stay unflagged.
- New `evals/fixtures/demo-app`: a buildable app with 13 planted faults and a control, covered by regression tests.
- Official Impeccable is optional.

## v2.2.0 - 2026-10-30

Ideas adapted from five MIT-licensed design skills (credited in `research/sources.md`).
- New lint rule **D011** (hype copy: unlock, seamless, supercharge, "Oops"...) for Kotlin, layouts and `strings.xml`; 40 rules.
- `anti-slop.md`: dated 2025-2026 tells in Android form (warm-editorial shortcut, eyebrow labels, pill badges, accented word, mono as costume, index numbering, decorative status dots, fake dashboards, invented proof) and the "removal is not enough" rule. From taste-skill and Hallmark.
- `product-brief.md`: brand-truth protocol, never theme a real brand from memory. From Hallmark.
- `master-critique.md`: cover-the-logo, edges, sameness and collisions passes; fix order; fresh-eyes review by a sub-agent that did not build the screen. From taste-skill and Hallmark.

## v2.1.0 - 2026-10-29

- **Master critique** (`critique` mode at full depth): capture -> design review before tools -> deterministic scan -> Craft Score -> report -> targeted questions -> action plan. New module `modules/09-verify/master-critique.md` with Android personas (Casey, Sam, Rita, Alex, Riley) and a cognitive-load / Nielsen cross-check.
- New `scripts/critique_score.py`: Craft Score 0-100 from evidence-backed rubric scores, published weights, P0/P1 caps, confidence from visual coverage, grade bands, archive and trend (`--save`).
- New `assets/CRITIQUE_TEMPLATE.json`; `critique quick` keeps the short version.
- README scorecard image generated from real script output; 51 tests.

## v2.0.0 - 2026-10-29

**Architecture**
- SKILL.md rewritten as a 167-line router (principles, craft loop, 24 modes, module index, official-skill hand-offs).
- 30 modules in 11 groups (discover, direction, system, layout, components, motion, accessibility, performance, verify, platforms, agents) + research ledger. All links one level deep; long files have a Contents section.
- Repository layout for plugin marketplaces (`.claude-plugin/`, `.codex-plugin/`).

**New knowledge**
- 10 named aesthetic anchors; Android anti-slop catalogue with lint ids; squint test.
- Design system modules: color roles, contrast levels (API 34), dark theme, semantic/extended colors; M3 type scale, tabular numerals, 200% scaling, line breaking; shape/space/elevation tokens; iconography, app icon, images; theming code incl. Expressive and Styles API gates.
- Layout, edge-to-edge (SDK 35/36), adaptive (window size classes incl. large/xl, SDK 36/37 large-screen rules), navigation and predictive back, components catalogue, forms/IME/autofill, states and haptics, UX copy and i18n/RTL, data display.
- Motion system with MotionScheme springs; accessibility semantics recipes and manual scripts; performance method with honest reporting.
- Visual feedback loop, device matrix, screenshot testing, critique rubric (10 dimensions, no averaged score), release gates with `incomplete` decision.
- Form factors (Wear, TV, Cars, XR, widgets, notifications) and toolkit map (Views, Flutter, React Native, CMP).
- Agent setup for Claude Code, Codex, Antigravity (Gemini CLI replaced for many tiers in June 2026), always-on AGENTS snippet.

**Tools**
- `ui_audit.py lint`: 39 rules, suppression comments, Markdown/JSON/SARIF, `--fail-on`. `palette`: WCAG check of every role pair in Kotlin schemes. `contrast`: `#AARRGGBB` compositing.
- `project_probe.py`: SDK levels, Compose BOM, Material 3, Kotlin, libraries, toolkit verdict, manifest flags, platform mandates.
- New `device_matrix.py` (14 profiles, adb, restore and `--restore-only`), `validate_skill.py`.
- `review_gate.py` v2 schema (states, adaptive, `not_applicable`, P0-P3 issues, decision levels), still accepts v1 reports.
- Templates: `CraftTheme.kt`, `CraftPreviews.kt`, `A11yCheckTest.kt`, `DESIGN_TEMPLATE.md`, `AGENTS_SNIPPET.md`.
- `evals/` with 9 scenarios and a sloppy fixture app; 42 unit tests.

**Changed**
- Dark-only is no longer a default; it is one anchor (Tonal Calm) among ten.
- Modes `touch/space/harden/accessibility` kept; overlapping guidance consolidated into modules.

## v1.2 - 2026-10-28
- Evidence states PASS/FAIL/NOT RUN; accessibility, visual-regression, performance and release-review modes; version-aware screenshot strategy; `project_probe.py`; `review_gate.py`.

## v1.1 - 2026-10-28
- Research references, video study, Codex/Gemini/Claude install.

## v1.0 - 2026-10-28
- Native Android critique/redesign/touch/space/animate/audit flow with static scanner.
