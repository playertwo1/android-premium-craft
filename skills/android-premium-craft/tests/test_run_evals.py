import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'evals'))
import run_evals  # noqa: E402


class PrepareTests(unittest.TestCase):
    def scenario(self, sid):
        return next(s for s in run_evals.scenarios() if s['id'] == sid)

    def test_arms_and_hint_removal(self):
        sc = self.scenario('critique-sloppy-home')
        with tempfile.TemporaryDirectory() as tmp:
            with_dir, without_dir = Path(tmp) / 'a', Path(tmp) / 'b'
            run_evals.prepare(with_dir, sc, 'with')
            run_evals.prepare(without_dir, sc, 'without')
            self.assertTrue((with_dir / 'CLAUDE.md').exists())
            self.assertTrue((with_dir / '.claude/skills/android-premium-craft/SKILL.md').exists())
            self.assertFalse((with_dir / '.claude/skills/android-premium-craft/evals').exists())
            self.assertFalse((without_dir / 'CLAUDE.md').exists())
            for root in (with_dir, without_dir):
                kt = next((root / 'app').rglob('HomeScreen.kt')).read_text(encoding='utf-8')
                self.assertNotIn('Deliberately sloppy', kt)

    def test_prepare_wipes_previous_run(self):
        sc = self.scenario('negative-backend')
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / 'w'
            work.mkdir()
            (work / 'stale.txt').write_text('x')
            run_evals.prepare(work, sc, 'without')
            self.assertFalse((work / 'stale.txt').exists())


if __name__ == '__main__':
    unittest.main()
