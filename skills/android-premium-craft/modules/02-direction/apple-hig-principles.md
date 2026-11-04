# Apple HIG principles, built on Android

Apple's Human Interface Guidelines (HIG) are the clearest public statement of restraint: content first, one accent, hierarchy from size and weight, motion that is brief and cancelable. Asking for that quality bar produces more elegant apps than "clean and modern". This module distills the HIG (read 2026-11-03, after the June 2026 revision that reintroduced the design principles) into rules an Android app can follow **with Material components**. Borrow the judgment, never the look: an Android app that imitates iOS fails users' platform expectations and the `platform` rubric dimension.

## Contents
- The eight principles, translated
- Rules by area (hierarchy, color, type, depth, motion, feedback, words, modals, brand)
- Numbers: iOS to Android
- Do not port
- HIG pass for critique and polish

## The eight principles, translated

| HIG principle | What it means on an Android screen |
|---|---|
| **Purpose**: make something meaningful | Name the one job of the screen; the features that serve it get the craft, the rest gets cut or moved behind disclosure |
| **Agency**: let people do things their way | Get people straight to the content; skippable guided flows; undo instead of confirm for reversible actions; predictive back always works |
| **Responsibility**: act in people's interest | Ask for a permission at the moment of use with a one-line reason; collect only what the feature needs |
| **Familiarity**: build on what people know | Standard Material components in standard places; one behavior per element across the app; system patterns for alerts and choices |
| **Flexibility**: adapt to contexts and needs | Light, dark, contrast levels, 200% text, RTL, keyboard and TalkBack from the start; window size classes, not device type, decide layout |
| **Simplicity**: be clear and direct | "Simplicity isn't minimalism": keep the important things close and let the others fall away; every element earns its place |
| **Craft**: care about every detail | Alignment, wording, motion and states are deliberate; prototype, look at the pixels, iterate; keep current with the platform |
| **Delight**: make it human | Pick the emotion (calm, energy, trust) and design one or two defining moments around it; delight is not decoration |

## Rules by area

**Hierarchy and layout**
- Order by importance in reading order: top and leading side first. Keep that order at every font size.
- Align to few keylines; indent to show subordination. Group with space first, then a container or a divider, never all three.
- Progressive disclosure: secondary details and actions one tap away (overflow menu, expandable row, detail screen), not all on screen.
- Separate controls from content: content scrolls under the app bar and navigation bar, which stay legible. On Android this is the M3 `TopAppBar` `scrollBehavior` (container color change on scroll) and edge-to-edge content, not a fake glass layer.
- Full-bleed media extends under the system bars and app bar; scrims keep labels legible.
- Larger windows show more of the same functionality (navigation bar to rail, overflow to visible actions); the functions never change with size.

**Color**
- One accent, used on the **background** of the primary action, the selected navigation item and status badges. Not on headings, not on several buttons in one region.
- One color, one meaning: if the accent marks interactivity, non-interactive text never uses it.
- Semantic roles only, never repurposed: `outlineVariant` is not a text color, `onSurfaceVariant` is not a background. The iOS label levels map to `onSurface` then `onSurfaceVariant`; the system, grouped and elevated backgrounds map to `surface`, `surfaceContainerLow` and `surfaceContainer..Highest`.
- Every custom color ships light, dark and higher-contrast variants. Dark colors are not inversions: dimmer backgrounds, brighter foregrounds, elevated layers lighter than the base.
- Over colorful content, keep bars and their labels monochrome; reserve brand color for the content layer.
- Contrast: 4.5:1 minimum for text; HIG asks to strive for **7:1 for small custom text**. Check under sunlight and in a dark room, not only in a calculator.
- Soften white-background images in dark theme (slight dim) so they do not glow.

**Typography**
- Minimize typefaces: the system font, or one brand face for headlines and subheadings with the system font for body and captions.
- Avoid thin and light weights; hierarchy from regular, medium, semibold and bold plus size and color.
- When text grows, the content grows first; tabs and chrome need not. Stack side-by-side items, drop columns, let rows grow, and show as much text at 200% as at 100% instead of truncating.
- Loose line height for long passages; tight only for one or two lines, never for three or more.
- A large, bold screen title that yields to a compact title on scroll (`LargeTopAppBar` or `MediumFlexibleTopAppBar` with `exitUntilCollapsedScrollBehavior`) is the Android form of the HIG large title.

**Depth and materials**
- Two layers: content, and a functional layer (bars, FAB, floating toolbar) above it. Translucency or blur only on the functional layer and only where content scrolls beneath; never in the content layer.
- Choose a surface by meaning (grouping, elevation), not by the tint it gives. Thicker (more opaque) for text-heavy panels, thinner only over rich media, with a dim of about 35% when the media is bright.
- Respect reduce-transparency and contrast settings: a blurred bar falls back to an opaque container.

**Motion**
- Motion only with a purpose: feedback, orientation, status. Never as the only carrier of information; pair with text, haptics or sound.
- Brief and precise; follow the gesture (a view pulled down is dismissed down, not sideways).
- No animation on interactions people repeat many times a day beyond what the components already do.
- Always cancelable and interruptible; never wait on an animation to accept input.

**Feedback, loading and launch**
- Match the interruption to the importance: passive status inline near the item it describes, a snackbar for results, a dialog only for critical and actionable information.
- Warn only before unexpected, irreversible data loss; deleting something the user chose to delete gets undo, not a confirm dialog.
- Confirm completion only for significant tasks (a payment); say why a command cannot run.
- Show something immediately: placeholders shaped like the content, then content. Determinate progress when the duration is known.
- The launch (`SplashScreen` API) looks like the first screen: no text, no advertising. Restore the previous state and scroll position on return.
- Onboarding is optional, short and interactive; prefer contextual tips near the feature. Defer setup and ratings until people have used the app.

**Words**
- A defined voice; tone shifts with the moment (payment error: direct; goal reached: warm).
- Buttons are verbs ("Send", not "Let's do it!"); links say where they go, never "Click here".
- No "we" in errors ("Unable to load content", not "We're having trouble..."); no "oops". Errors sit next to the problem and say how to fix it ("Choose a password with at least 8 characters").
- Sparing possessives ("Favorites", not "Your Favorites"); one capitalization style per element type; "Get started", "Continue", "Done" used consistently across multi-step flows.
- Empty states give a next step with a button; settings say what happens when on; link straight to a setting instead of describing its path.

**Modals**
- Modal only with a clear benefit; short, single-path, titled with its task. Never stack modals; never two dialogs at once.
- Every modal has an obvious dismissal (back, swipe down on a sheet, a close action). Unsaved input prompts before it is lost.
- Complex or long tasks get a full screen, not a sheet.

**Brand**
- Branding defers to content: no logo repeated on screens, no splash-as-billboard. Brand lives in the accent, the voice, one headline face and the content layer.
- Express the brand with familiar components; customize appearance but keep the size, placement and behavior people expect.

## Numbers: iOS to Android

HIG points and Android dp are both density-independent; use the Android value.

| HIG (iOS) | Android equivalent |
|---|---|
| Default control 44x44pt, minimum 28x28pt | 48x48dp touch target (`minimumInteractiveComponentSize()`); visual can be smaller |
| ~12pt padding around bezeled controls, ~24pt around borderless ones | 8dp minimum between targets; 12-24dp breathing room for a premium feel |
| Body 17pt, minimum 11pt | `bodyLarge` 16sp; nothing below 12sp, 14sp for content |
| Large Title 34 / Title 1 28 / Title 2 22 / Headline 17 semibold | `displaySmall` 36 / `headlineMedium` 28 / `titleLarge` 22 / `titleMedium` 16 medium |
| Text enlarges to at least 200% | Font scale 2.0 without loss of content or function |
| Dim of 35% under clear glass over bright media | Scrim of about 35% black under overlays on bright imagery |

## Do not port

These are iOS conventions; on Android they read as a foreign app.
- SF Pro or New York fonts (licensed for Apple platforms only), SF Symbols (use Material Symbols), Apple hardware drawings.
- Liquid Glass imitation everywhere, iOS-style switches, segmented controls styled as iOS, trailing chevrons on every row.
- A left-pointing back chevron with text, custom left-edge swipe-back, "Cancel / Done" sheet headers in place of predictive back and a primary action.
- A top-of-screen iOS tab bar look or a hidden bottom navigation; disabling navigation items instead of showing an empty state.
- Haptics: keep to Android `HapticFeedbackConstants` meanings (`CONFIRM`, `REJECT`, `SEGMENT_TICK`); the HIG rule that transfers is "consistent, sparing, optional".

## HIG pass for critique and polish

Run after the rubric pass; each "no" is a polish finding unless it blocks a task.
- [ ] Is there one primary action, and is the accent only on it, the selected destination and badges?
- [ ] Does the content come before the chrome (no logo bars, no decorative header)?
- [ ] Is hierarchy readable from size and weight alone, in grayscale?
- [ ] Do controls stay legible above scrolling content, and is that done with standard components?
- [ ] Are secondary actions one tap away instead of all visible?
- [ ] Does every animation have a purpose and stop on touch?
- [ ] Is the interruption level right for each message (inline, snackbar, dialog)?
- [ ] Do button labels use verbs and errors say how to fix the problem, without "we" or "oops"?
- [ ] Does it still look intentional at 200% text and in dark theme with high contrast?
- [ ] Would a long-time Android user find every control where they expect it?

Sources: the HIG pages listed under "Apple Human Interface Guidelines" in [sources.md](../../research/sources.md).
