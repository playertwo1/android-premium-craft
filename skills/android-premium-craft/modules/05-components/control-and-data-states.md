# Control states, forms and data screens

Load with `harden`, `copy`, `polish`, or when a screen has a form, a list or numbers. Applies to Compose, Flutter and React Native. Complements [states-and-feedback.md](states-and-feedback.md). Ideas adapted from taste-skill and Hallmark (MIT), rewritten; see [sources](../../research/sources.md).

## Every control state

A control missing one of these is not finished. Verify on the capture, not in the code.

| State | Treatment |
|---|---|
| Default | Base theme style |
| Pressed | One signal: native ripple or one tonal step |
| Focus | Visible with keyboard, D-pad and screen reader; never removed without a replacement |
| Selected | Shape or weight besides color; color is never the only signal |
| Disabled | Readable, with the reason nearby; no 30% opacity on text that must be read |
| Loading | Progress inside the control; the label stays readable and the width does not jump |
| Error | Error color + message + icon; announced by the screen reader |
| Success | The result itself, only after a real response; no success where nothing was requested |

## Forms

- Visible label above or in the field; a placeholder shows the format and never replaces the label.
- Validate when leaving a touched field; once an error shows, re-validate on each keystroke.
- One-sentence error: what broke, why, what to do. It replaces helper text on the same line without pushing the layout.
- Right keyboard per field, Next/Done action and autofill.
- Disable submit only while the request runs, never at rest.
- Primary button visible with the keyboard open; one filled primary per screen.
- Settings: one way to save per screen (each control saves with a quiet notice, or one Save). Never both.
- Destructive action last, separated, with the consequence in words.

## Zero, empty, loading, error and stale data

- **Real zero** uses the normal style ("R$ 0,00"). **Missing** is a quiet dash, never "--" at value size, which reads as loading.
- **Empty section** keeps its frame and title and gains one sentence plus an action when there is one. Never just "No results" or a generic illustration.
- **First use** keeps title and structure; the first action sits where the data will appear; setup progress shows the real percentage.
- **Loading** is the final layout with flat bars at the real value size and labels already visible, no flashy shimmer, no jump when data arrives. Refreshing keeps the old values on screen.
- **Error** stays inside the block that failed: what failed, when the data was last good, and Retry.
- **Offline or stale** shows a visible update stamp; never fake live data.
- **Red is a signal, not a texture**: at most one red mark per item, on the fact that is wrong.
- **Counts follow the filter** and recalculate on every tab or filter change.

## Data screens on a phone

- The title asks a question; the largest element answers it and is read first.
- Numbers: right-aligned, tabular, fixed decimals, quiet unit. Totals match the rows.
- A change states its base ("+4 since yesterday"); zero or no change stays neutral, not green.
- Tables become two-line lists: identity and main number on line 1, smaller fields on line 2, one action on the right. Fields wrap, they do not vanish. The page never scrolls sideways.
- At most one filter row above the list; the first item starts in the top 60% of the screen.
- KPIs in a 2-column grid or label/value list; never four squeezed columns or an orphan cell.
- Charts: one color per series, 3-4 axis labels, a legend only with more than one series.
- List and detail: one region at a time on compact; back returns to the same scroll position.

**Generated dashboard tells:** "Hi, Name 👋" on top; four KPIs with an icon in a colored circle; a green "+12.5%" pill on every KPI; a sparkline in every card; rainbow chart; thick donut with the total inside; accent on every tab and button; round sample data (Acme, "10,000+"). Replace them with the product's real data at real size, with sums that add up.

## Dark theme: parity, not inversion

- Tinted dark background, not `#000` (except a deliberate OLED mode); tinted light text, not pure `#FFF`.
- Elevation through lighter surfaces, not shadow; a card is lighter than the background, never darker.
- Accent slightly less saturated and lighter; recheck text contrast on it.
- The brand hue does not change between themes. Each contrast pair applies to both: check the theme you did not capture numerically.
- Images are not inverted; pick versions that work on dark.

## Capture checklist

1. Does the largest element answer the screen's question?
2. Do all blocks share the same edges? Any dead strip or a card that ends early?
3. Is color only on data, status and the primary action?
4. Do numbers add up and align digit by digit? Do repeated facts have the same value?
5. Does every zero look like zero and every missing value like a dash?
6. Does each control have the states in the table above?
7. At 200% text, with the keyboard open and in dark theme, does the screen still answer its question?

Fix the worst three, capture again, two loops at most.
