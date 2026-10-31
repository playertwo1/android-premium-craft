# Demo Caixa: planted faults

Fictional data only. Build with `./gradlew :app:assembleDebug`; needs `local.properties` or `ANDROID_HOME`.

| Id | Fault | Found by |
|---|---|---|
| F1 | Material sample purple | D010 |
| F2 | `onPrimary` without contrast | `palette` (2.05:1) |
| F3 | Emoji in title | D004 |
| F4 | Search button with no accessible name | A001, view tree |
| F5 | `innerPadding` ignored; balance hidden under the bar | L001, capture |
| F6 | Gradient background | D005 |
| F7 | 10sp text faded with alpha | T001, C004 |
| F8 | Card in card, with shadow | D002, D003 |
| F9 | Fixed height on text; hype copy | A006, D011 |
| F10 | 24dp target that clears the list | A003 |
| F11 | List without key; no empty state | P001; empty state only on capture |
| F12 | Locked orientation | L004 |
| F13 | Not resizable | L005 |

Control: the Add button has a `contentDescription` and must not trigger A001. Tapping "Limpar" shows the blank empty state.
