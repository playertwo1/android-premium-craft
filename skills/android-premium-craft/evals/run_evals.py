#!/usr/bin/env python3
"""Minimal eval runner: isolated workspaces, with/without arms, blinded review.

  python evals/run_evals.py run   --out DIR [--reps 3] [--scenarios id,...] [--arms with,without] [--jobs 4]
  python evals/run_evals.py score --out DIR [--reviewer-model claude-opus-5-5]
  python evals/run_evals.py report --out DIR

Each run gets an opaque id and its own folder under OUT/runs/<id>/work. The runner deletes that
folder when preparing, so one OUT must never be used by two instances: OUT/.lock enforces it.
The arm is recorded only in OUT/manifest.json; the reviewer sees neither ids, arms nor paths.
Run it from a neutral --out path (no project name in it). Bash is limited to the BASH allowlist (each piece of a compound command is checked); runs are not otherwise sandboxed.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import secrets
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
EVALS = SKILL / 'evals'
NAME = 'android-premium-craft'
CLAUDE_FLAGS = ['--setting-sources', 'project', '--strict-mcp-config', '--no-session-persistence',
                '--output-format', 'stream-json', '--verbose']
# Compound commands are checked piece by piece, so every piece needs an entry.
BASH = ['python', 'python3', 'py', 'cd', 'ls', 'cat', 'head', 'tail', 'grep', 'find', 'wc', 'echo', 'mkdir', 'sort', 'diff']
TOOLS = ','.join(['Read', 'Edit', 'Write', 'Glob', 'Grep', 'Skill'] + [f'Bash({c}:*)' for c in BASH])
IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '.pytest_cache', 'evals', 'tests')
# Criteria (index per scenario) that name the skill's own artifacts; reported separately.
SKILL_SPECIFIC = {'critique-sloppy-home': [0, 1, 2], 'release-review-no-device': [0, 1],
                  'shape-finance-dashboard': [1], 'build-settings-screen': [2], 'adapt-tablet': [4]}


def scenarios() -> list[dict]:
    return json.loads((EVALS / 'evals.json').read_text(encoding='utf-8'))


def prepare(work: Path, scenario: dict, arm: str) -> None:
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for rel in scenario['files']:
        src = SKILL / rel
        if src.is_dir():
            shutil.copytree(src, work, dirs_exist_ok=True, ignore=IGNORE)
        else:
            shutil.copy2(src, work / src.name)
    for kt in work.rglob('HomeScreen.kt'):  # the comment gives the answer away
        kt.write_text(re.sub(r'^// Deliberately sloppy.*\n', '', kt.read_text(encoding='utf-8'), flags=re.M), encoding='utf-8')
    if arm == 'with':
        shutil.copytree(SKILL, work / '.claude' / 'skills' / NAME, ignore=IGNORE)
        shutil.copy2(SKILL / 'assets' / 'AGENTS_SNIPPET.md', work / 'CLAUDE.md')


def snapshot(work: Path) -> dict[str, bytes]:
    return {p.relative_to(work).as_posix(): p.read_bytes() for p in work.rglob('*')
            if p.is_file() and '.claude' not in p.parts and p.name != 'CLAUDE.md'}


def run_one(out: Path, rid: str, entry: dict, scenario: dict, model: str, timeout: int, budget: float) -> None:
    work = out / 'runs' / rid / 'work'
    prepare(work, scenario, entry['arm'])
    before = snapshot(work)
    env = {k: v for k, v in os.environ.items() if k != 'CLAUDECODE'}
    cmd = [shutil.which('claude') or 'claude', '-p', scenario['query'], '--model', model, '--allowedTools', TOOLS, '--disallowedTools', 'PowerShell,WebFetch,WebSearch',
           '--max-budget-usd', str(budget), *CLAUDE_FLAGS]
    raw = out / 'runs' / rid / 'stream.jsonl'
    try:
        proc = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, timeout=timeout,
                              encoding='utf-8', errors='replace')
        raw.write_text(proc.stdout, encoding='utf-8')
        status = 'ok' if proc.returncode == 0 else f'exit {proc.returncode}'
    except subprocess.TimeoutExpired as e:
        raw.write_text((e.stdout or b'').decode('utf-8', 'replace') if isinstance(e.stdout, bytes) else (e.stdout or ''), encoding='utf-8')
        status = 'timeout'
    after = snapshot(work)
    changed = {k: v.decode('utf-8', 'replace') for k, v in after.items() if before.get(k) != v}
    (out / 'runs' / rid / 'changed.json').write_text(json.dumps(changed, ensure_ascii=False), encoding='utf-8')
    entry['status'] = status
    print(f'{rid} {status}', flush=True)


def events(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding='utf-8').splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def summarize(out: Path, rid: str) -> dict:
    ev = events(out / 'runs' / rid / 'stream.jsonl')
    init = next((e for e in ev if e.get('subtype') == 'init'), {})
    result = next((e for e in reversed(ev) if e.get('type') == 'result'), {})
    skill_loaded = any(b.get('type') == 'tool_use' and b.get('name') == 'Skill'
                       and NAME in json.dumps(b.get('input', {}))
                       for e in ev if e.get('type') == 'assistant' for b in e['message']['content'] if isinstance(b, dict))
    blocked = sum(1 for e in ev if e.get('type') == 'user' for b in e['message']['content']
                  if isinstance(b, dict) and b.get('is_error') and re.search(r'requires approval|was blocked|permission', json.dumps(b.get('content'))))
    return {'blocked': blocked, 'skill_loaded': skill_loaded, 'skills_in_init': init.get('skills', []), 'final': result.get('result', ''),
            'cost': result.get('total_cost_usd'), 'turns': result.get('num_turns'), 'error': result.get('is_error', True)}


def sanitized_view(out: Path, rid: str) -> str:
    """Final reply, tool calls and written files, with paths and skill loading removed."""
    ev = events(out / 'runs' / rid / 'stream.jsonl')
    root = re.escape(str(out / 'runs' / rid / 'work'))
    clean = lambda s: re.sub(r'(?i)[^\s"\']*\.claude[/\\]skills[/\\]' + NAME, '<tools>', re.sub(root, '.', s, flags=re.I)).replace('\\', '/')
    lines = []
    for e in ev:
        if e.get('type') != 'assistant':
            continue
        for b in e['message']['content']:
            if b.get('type') == 'tool_use' and b['name'] != 'Skill':
                lines.append(clean(f"[{b['name']}] {json.dumps(b['input'], ensure_ascii=False)[:600]}"))
    changed = json.loads((out / 'runs' / rid / 'changed.json').read_text(encoding='utf-8'))
    files = '\n\n'.join(f'--- {k}\n{v[:6000]}' for k, v in changed.items())
    final = summarize(out, rid)['final']
    return clean(f'## Final reply\n{final}\n\n## Tool calls\n' + '\n'.join(lines[:80]) + f'\n\n## Files created or changed\n{files}')


def cmd_run(a) -> None:
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    try:
        lock = os.open(out / '.lock', os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        sys.exit(f'{out} is locked by another run. Use a different --out (delete .lock only if no runner is alive).')
    try:
        os.write(lock, str(os.getpid()).encode())
        chosen = a.scenarios.split(',') if a.scenarios else None
        scs = {s['id']: s for s in scenarios() if not chosen or s['id'] in chosen}
        manifest = json.loads((out / 'manifest.json').read_text()) if (out / 'manifest.json').exists() else {}
        for sid in scs:
            for arm in a.arms.split(','):
                for rep in range(a.reps):
                    if not any(m['scenario'] == sid and m['arm'] == arm and m['rep'] == rep for m in manifest.values()):
                        manifest[secrets.token_hex(4)] = {'scenario': sid, 'arm': arm, 'rep': rep, 'status': 'pending'}
        todo = [(r, m) for r, m in manifest.items() if m['status'] != 'ok']
        with ThreadPoolExecutor(a.jobs) as pool:
            futs = [pool.submit(run_one, out, r, m, scs[m['scenario']], a.model, a.timeout, a.budget)
                    for r, m in todo if m['scenario'] in scs]
            for f in futs:
                f.result()
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
    finally:
        os.close(lock)
        (out / '.lock').unlink(missing_ok=True)


REVIEW = """You score one agent run against a rubric. Be strict: a criterion is met only if the material below shows it.
Do not guess which setup produced the run.

Task given to the agent: {query}

Criteria:
{criteria}

Material:
{material}

Answer with JSON only: {{"scores": [{{"criterion": 1, "met": true, "why": "<one line>"}}, ...]}} covering every criterion."""


def cmd_score(a) -> None:
    out = Path(a.out).resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    scs = {s['id']: s for s in scenarios()}
    env = {k: v for k, v in os.environ.items() if k != 'CLAUDECODE'}
    rids = [r for r, m in manifest.items() if m['status'] == 'ok' and 'score' not in m]
    random.shuffle(rids)
    review_dir = out / 'review'  # neutral folder, no run names

    def score(rid: str) -> None:
        s = scs[manifest[rid]['scenario']]
        crit = '\n'.join(f'{i + 1}. {c}' for i, c in enumerate(s['expected_behavior']))
        prompt = REVIEW.format(query=s['query'], criteria=crit, material=sanitized_view(out, rid))
        review_dir.mkdir(exist_ok=True)
        p = subprocess.run([shutil.which('claude') or 'claude', '-p', '--model', a.reviewer_model, '--tools', '', '--max-budget-usd', '1',
                            '--setting-sources', 'project', '--strict-mcp-config', '--no-session-persistence'],
                           cwd=review_dir, env=env, input=prompt, capture_output=True, text=True, timeout=600, encoding='utf-8', errors='replace')
        m = re.search(r'\{.*\}', p.stdout, re.S)
        try:
            manifest[rid]['score'] = [bool(x['met']) for x in json.loads(m.group(0))['scores']]
            manifest[rid]['why'] = [x.get('why', '') for x in json.loads(m.group(0))['scores']]
        except (AttributeError, ValueError, KeyError):
            print(f'{rid}: unparsable review', flush=True)

    with ThreadPoolExecutor(a.jobs) as pool:
        list(pool.map(score, rids))
    for r, m in manifest.items():
        if m['status'] == 'ok':
            m.update({k: v for k, v in summarize(out, r).items() if k in ('skill_loaded', 'cost', 'turns', 'blocked')})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')


def cmd_report(a) -> None:
    out = Path(a.out).resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    scs = {s['id']: s for s in scenarios()}
    tot = {'with': [0, 0, 0, 0], 'without': [0, 0, 0, 0]}  # met, possible, met excl. skill-specific, possible excl.
    print('| Scenario | Skill loaded (with) | With | Without |\n|---|---:|---:|---:|')
    for sid, s in scs.items():
        cells = {}
        for arm in ('with', 'without'):
            runs = [m for m in manifest.values() if m['scenario'] == sid and m['arm'] == arm and 'score' in m]
            met = sum(sum(m['score']) for m in runs)
            poss = sum(len(m['score']) for m in runs)
            skip = SKILL_SPECIFIC.get(sid, [])
            t = tot[arm]
            t[0] += met; t[1] += poss
            t[2] += sum(v for m in runs for i, v in enumerate(m['score']) if i not in skip)
            t[3] += sum(1 for m in runs for i, _ in enumerate(m['score']) if i not in skip)
            cells[arm] = f'{met}/{poss}'
        loaded = [m for m in manifest.values() if m['scenario'] == sid and m['arm'] == 'with' and m['status'] == 'ok']
        print(f"| {sid} | {sum(bool(m.get('skill_loaded')) for m in loaded)}/{len(loaded)} | {cells['with']} | {cells['without']} |")
    for arm, t in tot.items():
        print(f'\n{arm}: {t[0]}/{t[1]} all criteria; {t[2]}/{t[3]} excluding skill-specific artifacts')
    cost = sum(m.get('cost') or 0 for m in manifest.values())
    print(f'\nruns: {len(manifest)}, ok: {sum(m["status"] == "ok" for m in manifest.values())}, cost: ${cost:.2f}')


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name, fn in (('run', cmd_run), ('score', cmd_score), ('report', cmd_report)):
        p = sub.add_parser(name)
        p.add_argument('--out', required=True, help='own folder per round; never share between instances')
        p.set_defaults(fn=fn)
        if name == 'run':
            p.add_argument('--reps', type=int, default=3)
            p.add_argument('--scenarios')
            p.add_argument('--arms', default='with,without')
            p.add_argument('--model', default='claude-sonnet-5-5')
            p.add_argument('--timeout', type=int, default=900, help='seconds per run')
            p.add_argument('--budget', type=float, default=2.0, help='USD per run')
        if name != 'report':
            p.add_argument('--jobs', type=int, default=3)
        if name == 'score':
            p.add_argument('--reviewer-model', default='claude-opus-5-5')
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
