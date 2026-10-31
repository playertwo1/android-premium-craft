# Mobile guideline tables

Copied without content changes from UI/UX Pro Max (https://github.com/nextlevelbuilder/ui-ux-pro-max-skill,
`src/ui-ux-pro-max/data`, commit 28b3b8d, 2026-10-26). Each row has `Do`, `Don't`, good and bad examples,
`Severity` and, in the stack tables, `Docs URL` and `Verified At`.

| File | Source | Use |
|---|---|---|
| `compose.csv` | `stacks/jetpack-compose.csv` | Jetpack Compose |
| `flutter.csv` | `stacks/flutter.csv` | Flutter |
| `react-native.csv` | `stacks/react-native.csv` | React Native / Expo |
| `app-interface.csv` | `app-interface.csv` | Cross-stack mobile UX (touch, accessibility, navigation, forms) |

Do not load a whole table. Filter it: `python scripts/mobile.py guidelines --stack compose --severity high --category Accessibility`.
Check `Verified At` before calling an API current.

MIT License - Copyright (c) 2024 Next Level Builder. Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions: The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED.
