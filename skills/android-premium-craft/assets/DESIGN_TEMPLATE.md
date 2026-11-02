# DESIGN.md - <App name>

Source of truth for UI decisions. Agents read this before UI work; update it in the same change as the theme.

## Product
- Users and frequency:
- Top 3 jobs (one per key screen):
- Context of use (one-hand, outdoors, desk, glance):
- Domain register (see product-brief): ... -> must feel ..., must never ...

## Direction
- Anchor: <base> (+ <accent>)
- Because:
- Allowed:
- Not allowed:
- Themes supported: light / dark / dynamic color / contrast levels

## Tokens
### Color
| Role | Light | Dark | Notes |
|---|---|---|---|
| primary / onPrimary | | | Main action only |
| primaryContainer / onPrimaryContainer | | | |
| secondary / tertiary | | | |
| surface ramp | | | containerLowest..Highest |
| onSurface / onSurfaceVariant | | | secondary text = onSurfaceVariant |
| error | | | |
| success / warning (extended) | | | |
Contrast verified with `ui_audit.py palette`: <date, result>

### Typography
| Role | Family | Size/Line | Weight | Use |
|---|---|---|---|---|
| displaySmall | | 36/44 | | hero number |
| titleLarge | | 22/28 | | screen titles |
| bodyLarge | | 16/24 | | content |
| labelLarge | | 14/20 | 500 | buttons |
Numbers: tabular figures (`tnum`).

### Shape, space, elevation
- Shape set: small 8 / medium 12 / large 16 / extraLarge 28 (which components use which)
- Spacing scale: 2 4 8 12 16 24 32 48 (names)
- Screen margins: compact 16, medium+ 24
- Elevation: tonal; shadows only on floating elements

### Motion
- Scheme: standard / expressive (where)
- Signature transition:
- Reduced motion behavior:

## Components
- Buttons: hierarchy rules
- Lists vs cards rule:
- Navigation per width class:
- Feedback: snackbar/undo rules, haptics map

## Content
- Voice: 3 adjectives + 3 rules
- Terminology list (one term per concept):

## Quality bar
- Device matrix profiles required: core
- Accessibility: TalkBack script on critical flows, 200% text, 48dp
- Screenshot tests: tool, configurations
- Performance: journeys measured and budgets

## Do and don't
- Do: (3-5 rules an agent must follow on every screen, in this app's words)
- Don't: (3-5 things this app never does, for example "no animated balances")

## Agent quick reference
| Need | Token or rule |
|---|---|
| Primary action | `colorScheme.primary` (one per screen) |
| Secondary text | `onSurfaceVariant` |
| Spacing | (list the named steps) |
| Heading / body | (list the type roles) |
Prompt examples: "Add a <component> using only these tokens", "Review <screen> against Do and don't".

## Known gaps
What this file does not know yet: unconfirmed values, substitute fonts, brand colors without a source, states not designed. Mark each as `unknown` instead of guessing.

## Decisions and exceptions
| Date | Decision | Why | Approved by |
|---|---|---|---|
