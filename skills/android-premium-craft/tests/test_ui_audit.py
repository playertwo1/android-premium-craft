import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from ui_audit import (RULES, as_markdown, contrast_ratio, lint, lint_markdown, lint_sarif, lint_text,  # noqa: E402
                      palette, palette_markdown, parse_color, parse_hex_color, summarize)
from ui_audit import main as ui_main  # noqa: E402

FIXTURE = ROOT / 'evals' / 'fixtures' / 'sloppy-app'
DEMO = ROOT / 'evals' / 'fixtures' / 'demo-app'


class PlantedFaultTests(unittest.TestCase):
    """The buildable demo app: see evals/fixtures/demo-app/PLANTED.md."""

    def test_every_code_fault_is_found(self):
        found = {f['rule'] for f in lint(DEMO)['findings']}
        planted = {'D010', 'D004', 'A001', 'L001', 'D005', 'T001', 'C004', 'D002', 'D003', 'A006', 'D011', 'A003', 'P001', 'L004', 'L005'}
        self.assertEqual(planted - found, set())

    def test_correct_button_is_not_flagged(self):
        source = (DEMO / 'app/src/main/java/com/example/demo/MainActivity.kt').read_text(encoding='utf-8').splitlines()
        lines = [f['line'] for f in lint(DEMO)['findings'] if f['rule'] == 'A001']
        self.assertEqual(len(lines), 1)
        self.assertIn('Search', source[lines[0] - 1])

    def test_alpha_scrim_background_is_not_secondary_text(self):
        ids = {f.rule for f in lint_text('Box(Modifier.background(Color.Black.copy(alpha = 0.5f)))', 'app/x.kt', '.kt')}
        self.assertNotIn('C004', ids)

    def test_theme_contrast_failure_is_found(self):
        self.assertRegex(palette_markdown(palette(DEMO)), r'onPrimary \| primary \| 2\.05:1 \| 4\.5 \| \*\*FAIL\*\*')


class HypeCopyTests(unittest.TestCase):
    def ids(self, text, suffix):
        return {f.rule for f in lint_text(text, 'app/src/main/x' + suffix, suffix)}

    def test_flags_generated_copy(self):
        self.assertIn('D011', self.ids('Text("Unlock seamless banking")', '.kt'))
        self.assertIn('D011', self.ids('<string name="err">Oops! Something went wrong</string>', '.xml'))

    def test_plain_copy_passes(self):
        self.assertNotIn('D011', self.ids('Text("Pay R$ 40 to Ana")', '.kt'))
        self.assertNotIn('D011', self.ids('val elevated = Modifier.elevation(2.dp)', '.kt'))


class ContrastTests(unittest.TestCase):
    def test_white_black(self):
        self.assertAlmostEqual(contrast_ratio('#ffffff', '#000000'), 21.0, places=5)

    def test_same_color(self):
        self.assertAlmostEqual(contrast_ratio('#123456', '#123456'), 1.0, places=6)

    def test_shorthand(self):
        self.assertEqual(parse_hex_color('#fff'), parse_hex_color('#ffffff'))

    def test_invalid(self):
        for bad in ('#12345', 'blue', '#GGGGGG'):
            with self.assertRaises(ValueError):
                parse_color(bad)

    def test_symmetry_opaque(self):
        self.assertAlmostEqual(contrast_ratio('#FAFAFA', '#151515'), contrast_ratio('#151515', '#FAFAFA'))

    def test_alpha_is_composited(self):
        # 50% white over black is mid gray, far below pure white contrast.
        half = contrast_ratio('#80FFFFFF', '#000000')
        self.assertLess(half, 21.0)
        self.assertAlmostEqual(half, contrast_ratio('#808080', '#000000'), places=1)

    def test_kotlin_hex_form(self):
        self.assertEqual(parse_color('0xFF006A6A'), parse_color('#006A6A'))

    def test_translucent_background_rejected(self):
        with self.assertRaises(ValueError):
            contrast_ratio('#FFFFFF', '#80000000')


class LintTests(unittest.TestCase):
    def setUp(self):
        self.report = lint(FIXTURE)
        self.ids = {f['rule'] for f in self.report['findings']}

    def test_fixture_triggers_core_rules(self):
        expected = {'A001', 'A003', 'C001', 'C004', 'D002', 'D010', 'L001', 'L004', 'L005', 'L007', 'M001',
                    'N001', 'N004', 'P001', 'P002', 'P005', 'T001', 'X001', 'X003', 'X005'}
        self.assertTrue(expected <= self.ids, f'missing: {sorted(expected - self.ids)}')

    def test_rule_ids_unique_and_documented(self):
        ids = [r.id for r in RULES]
        self.assertEqual(len(ids), len(set(ids)))
        for r in RULES:
            self.assertTrue((ROOT / r.doc).is_file(), f'{r.id} points to missing {r.doc}')

    def test_sorted_by_severity(self):
        order = {'high': 3, 'medium': 2, 'low': 1}
        sev = [order[f['severity']] for f in self.report['findings']]
        self.assertEqual(sev, sorted(sev, reverse=True))

    def test_suppression_comment(self):
        code = 'val c = Color(0xFF112233) // craft-lint: ignore C001\nval d = Color(0xFF112233)\n'
        hits = [f.line for f in lint_text(code, 'ui/Screen.kt', '.kt') if f.rule == 'C001']
        self.assertEqual(hits, [2])

    def test_theme_files_may_define_colors(self):
        self.assertFalse([f for f in lint_text('val c = Color(0xFF112233)', 'ui/theme/Color.kt', '.kt') if f.rule == 'C001'])

    def test_small_target_only_when_interactive(self):
        self.assertFalse(lint_text('Icon(x, null, Modifier.size(24.dp))', 'a.kt', '.kt'))
        self.assertTrue([f for f in lint_text('Box(Modifier.size(24.dp).clickable { })', 'a.kt', '.kt') if f.rule == 'A003'])
        self.assertFalse([f for f in lint_text('Box(Modifier.size(48.dp).clickable { })', 'a.kt', '.kt') if f.rule == 'A003'])

    def test_keyed_items_not_flagged(self):
        self.assertFalse([f for f in lint_text('items(list, key = { it.id }) { }', 'a.kt', '.kt') if f.rule == 'P001'])

    def test_short_tween_not_flagged(self):
        self.assertFalse([f for f in lint_text('tween(200)', 'a.kt', '.kt') if f.rule == 'P005'])

    def test_comments_ignored(self):
        self.assertFalse(lint_text('// override fun onBackPressed() {', 'a.kt', '.kt'))

    def test_outputs(self):
        self.assertIn('Nothing was checked', lint_markdown(lint(Path(tempfile.mkdtemp()))))
        with tempfile.TemporaryDirectory() as td:
            Path(td, 'Clean.kt').write_text('val x = 1\n', encoding='utf-8')
            self.assertIn('does **not**', lint_markdown(lint(Path(td))))
            self.assertEqual(ui_main(['lint', td, '--fail-on', 'high']), 0)
        with tempfile.TemporaryDirectory() as td, redirect_stdout(io.StringIO()):
            self.assertEqual(ui_main(['lint', td, '--fail-on', 'high']), 1)  # a CI gate must not pass on nothing
        sarif = lint_sarif(self.report)
        self.assertEqual(sarif['version'], '2.1.0')
        self.assertEqual(len(sarif['runs'][0]['results']), len(self.report['findings']))
        json.dumps(sarif)


class PaletteTests(unittest.TestCase):
    def test_template_theme_passes(self):
        report = palette(ROOT / 'assets' / 'compose')
        names = {s['name'] for s in report['schemes']}
        self.assertTrue({'LightColors', 'DarkColors', 'LightExtended', 'DarkExtended'} <= names)
        self.assertTrue(all(s['failures'] == 0 for s in report['schemes']))

    def test_detects_failing_pair_and_resolves_named_colors(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td, 'Theme.kt').write_text(
                'val Brand = Color(0xFF9E9E9E)\n'
                'val Light = lightColorScheme(primary = Brand, onPrimary = Color(0xFFFFFFFF))\n', encoding='utf-8')
            scheme = palette(Path(td))['schemes'][0]
            self.assertEqual(scheme['roles']['primary'], '#FF9E9E9E')
            self.assertEqual(scheme['failures'], 1)


class LegacyScanTests(unittest.TestCase):
    def test_reports_hints_not_assertions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            src = root / 'app' / 'src' / 'main'
            src.mkdir(parents=True)
            (src / 'Main.kt').write_text('@Composable fun Main() {\n LazyColumn { }\n Text("Hi", fontSize = 10.sp)\n}',
                                         encoding='utf-8')
            report = summarize(root)
            ids = {f['code'] for f in report['findings']}
            self.assertIn('small_text_literals', ids)
            self.assertIn('window_insets', ids)
            self.assertIn('não', as_markdown(report).lower())

    def test_ignores_build_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'build').mkdir()
            (root / 'build' / 'Fake.kt').write_text('@Composable fun Wrong() {}')
            self.assertEqual(summarize(root)['summary']['source_files'], 0)


if __name__ == '__main__':
    unittest.main()
