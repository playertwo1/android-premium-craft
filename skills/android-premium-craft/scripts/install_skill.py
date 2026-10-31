#!/usr/bin/env python3
"""Copy this skill into a project's agent skill folders. --replace keeps the previous install as a backup."""
from __future__ import annotations

import argparse
import filecmp
import shutil
from datetime import datetime
from pathlib import Path

NAME = 'android-premium-craft'
AGENTS = ('claude', 'codex', 'antigravity', 'gemini')
IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '.pytest_cache')


def targets_for(project: Path, agents: list[str]) -> list[Path]:
    targets = []
    if any(agent in ('codex', 'antigravity', 'gemini') for agent in agents):
        targets.append(project / '.agents' / 'skills' / NAME)  # shared by Codex, Antigravity and Gemini CLI
    if 'claude' in agents:
        targets.append(project / '.claude' / 'skills' / NAME)
    return targets


def same_tree(left: Path, right: Path) -> bool:
    cmp = filecmp.dircmp(left, right, ignore=['__pycache__', '.pytest_cache'])
    _, mismatch, errors = filecmp.cmpfiles(left, right, cmp.common_files, shallow=False)
    return (not (cmp.left_only or cmp.right_only or cmp.common_funny or mismatch or errors)
            and all(same_tree(left / d, right / d) for d in cmp.common_dirs))


def install(source: Path, dst: Path, project: Path) -> Path | None:
    """Stage and verify the copy before touching dst; restore the old install if activation fails."""
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    label = dst.parts[-3]  # .claude or .agents; staging stays outside skill discovery folders
    stage = project / '.craft' / 'install-staging' / f'{label}-{stamp}'
    backup = project / '.craft' / 'install-backups' / f'{label}-{stamp}'
    shutil.copytree(source, stage, ignore=IGNORE)
    if not same_tree(source, stage):
        raise OSError(f'Copy verification failed; staged copy kept at {stage}')
    backed_up = dst.exists()
    if backed_up:
        backup.parent.mkdir(parents=True, exist_ok=True)
        dst.rename(backup)
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        stage.rename(dst)
    except OSError:
        if backed_up:
            backup.rename(dst)
        raise
    return backup if backed_up else None


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='Install Android Premium Craft into a project for Claude Code, Codex, Antigravity or Gemini CLI')
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--agents', nargs='+', choices=AGENTS, required=True)
    p.add_argument('--replace', action='store_true', help='Replace an existing install, keeping it under .craft/install-backups')
    a = p.parse_args(argv)
    project = a.project.expanduser().resolve()
    if not project.is_dir():
        p.error('--project must exist; the installer does not create repositories')
    source = Path(__file__).resolve().parent.parent
    if not (source / 'SKILL.md').is_file():
        p.error('Could not find SKILL.md next to the bundled scripts')
    paths = targets_for(project, a.agents)
    for dst in paths:
        # resolve() follows symlinks and junctions, so a linked skill folder cannot redirect the install.
        if project not in dst.resolve().parents:
            p.error(f'Target leaves the project through a link: {dst}')
        if dst.resolve() == source or source in dst.resolve().parents:
            p.error('Target must be outside the source folder')
    existing = [str(dst) for dst in paths if dst.exists()]
    if existing and not a.replace:
        p.error('Existing skill will not be replaced without --replace: ' + ', '.join(existing))
    for dst in paths:
        backup = install(source, dst, project)
        print('Installed:', dst)
        if backup:
            print('Previous install kept at:', backup)
    print('Add .craft/ to the app .gitignore: it holds captures, reports and install backups.')
    print('Tip: paste assets/AGENTS_SNIPPET.md into AGENTS.md / CLAUDE.md so the core rules apply even when the skill is not loaded.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
