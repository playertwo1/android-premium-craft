#!/usr/bin/env python3
"""Local-only Android screenshot, UI inspection, visual diff and Maestro runner.

Python 3.9+ and Pillow (capture, inspect, compare). No network calls, accounts or cloud services.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

DEFAULT_DIR = Path('.craft')


def command(args: list[str], timeout: int = 30, text: bool = True, cwd: Path | None = None):
    # CreateProcess does not resolve PATHEXT like shutil.which does.
    executable = shutil.which(args[0]) or args[0]
    argv = [executable, *args[1:]]
    # Windows can run batch files through cmd.exe even with shell=False.
    # Reject shell syntax instead of pretending list arguments make batches safe.
    if os.name == 'nt' and Path(executable).suffix.lower() in ('.bat', '.cmd'):
        if any(re.search(r'[&|<>^()%!"\r\n]', arg) for arg in argv):
            raise ValueError('Windows batch launchers do not accept shell metacharacters in arguments or paths. Use simple selectors or a native executable launcher.')
    try:
        return subprocess.run(argv, capture_output=True, check=False, timeout=timeout,
                              text=text, cwd=str(cwd) if cwd else None)
    except FileNotFoundError as ex:
        raise RuntimeError(f'Executable not found: {args[0]}') from ex
    except subprocess.TimeoutExpired as ex:
        raise RuntimeError(f'Timed out running: {args[0]}') from ex


def must_succeed(proc, label: str):
    if proc.returncode != 0:
        output = proc.stderr or proc.stdout
        if isinstance(output, bytes):
            output = output.decode('utf-8', 'replace')
        raise RuntimeError(f'{label} failed ({proc.returncode}): {str(output)[:1200]}')
    return proc


def adb(serial: str | None = None) -> list[str]:
    return ['adb'] + (['-s', serial] if serial else [])


def safe_name(raw: str) -> str:
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,70}', raw):
        raise ValueError('Allowed name: letters, digits, _ and - (1 to 70).')
    return raw


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def protect_outputs(paths: list[Path], overwrite: bool = False):
    for path in paths:
        if path.is_symlink():
            raise RuntimeError(f'Output cannot be a symbolic link: {path}')
        if path.exists() and (not overwrite or not path.is_file()):
            raise RuntimeError(f'Output already exists: {path}. Use another destination or --overwrite.')


def device_info(serial: str | None) -> dict:
    ret = {'serial': serial, 'collected_utc': utc_now()}
    props = {'model': 'ro.product.model', 'sdk': 'ro.build.version.sdk', 'android_release':'ro.build.version.release'}
    for key, prop in props.items():
        try:
            p = command(adb(serial) + ['shell','getprop',prop], timeout=10)
            ret[key] = p.stdout.strip() if p.returncode == 0 else None
        except RuntimeError:
            ret[key] = None
    for key, cmd in [('wm_size',['shell','wm','size']), ('wm_density',['shell','wm','density'])]:
        try:
            p=command(adb(serial)+cmd,timeout=10)
            ret[key]=p.stdout.strip() if p.returncode == 0 else None
        except RuntimeError:
            ret[key]=None
    return ret


def screenshot(path: Path, serial: str | None) -> dict:
    # adb exec-out emits unmodified PNG bytes, including on Windows.
    p = must_succeed(command(adb(serial) + ['exec-out','screencap','-p'], timeout=40,text=False), 'ADB screenshot')
    if not p.stdout.startswith(b'\x89PNG\r\n\x1a\n'):
        raise RuntimeError('adb did not return a valid PNG.')
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as ex:
        raise RuntimeError('Pillow is missing. Run pip install -r requirements.txt') from ex
    try:
        with Image.open(io.BytesIO(p.stdout)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError) as ex:
        raise RuntimeError('adb returned an incomplete or corrupt PNG.') from ex
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(p.stdout)
    info = device_info(serial)
    info.update({'image':str(path), 'bytes':len(p.stdout)})
    dump_json(path.with_suffix('.json'), info)
    return info


def cmd_devices(args):
    p=must_succeed(command(['adb','devices','-l']), 'adb devices')
    print(p.stdout)
    print('With more than one device, pass --serial SERIAL.')


def cmd_capture(args):
    name=safe_name(args.name)
    path=Path(args.output).absolute() if args.output else (DEFAULT_DIR/'captures'/f'{name}.png').absolute()
    if path.suffix.lower()!='.png':
        raise ValueError('The capture must use a .png extension')
    protect_outputs([path, path.with_suffix('.json')], args.overwrite)
    info=screenshot(path,args.serial)
    print(f'PNG capture saved: {path} ({info["bytes"]} bytes)')
    print('Warning: the image may contain personal data. Review before sharing.')


def cmd_inspect(args):
    name=safe_name(args.name)
    out=Path(args.output_dir).absolute() if args.output_dir else (DEFAULT_DIR/'inspections'/name).absolute()
    img=out/f'{name}.png'
    # Protect XML even if this invocation does not collect it: avoid mixing runs.
    protect_outputs([img, img.with_suffix('.json'), img.with_suffix('.xml')], args.overwrite)
    if img.with_suffix('.xml').exists() and not args.include_xml:
        raise RuntimeError('An earlier XML exists. Use another name so evidence is not mixed.')
    out.mkdir(parents=True,exist_ok=True)
    screenshot(img,args.serial)
    print(f'Screenshot saved: {img}')
    if args.include_xml:
        remote=f'/sdcard/__craft_{uuid4().hex}.xml'
        try:
            must_succeed(command(adb(args.serial)+['shell','uiautomator','dump',remote],timeout=45), 'uiautomator')
            p=must_succeed(command(adb(args.serial)+['exec-out','cat',remote],timeout=20,text=False), 'UI hierarchy')
            if b'<hierarchy' not in p.stdout:
                raise RuntimeError('XML dump has no hierarchy element. Capture again.')
            xml=out/f'{name}.xml'
            xml.write_bytes(p.stdout)
            print(f'XML dump saved: {xml}')
        finally:
            try:
                cleanup = command(adb(args.serial)+['shell','rm','-f',remote],timeout=15)
                must_succeed(cleanup, 'Temporary XML cleanup')
            except RuntimeError as ex:
                print(f'WARNING: {ex}; temporary file on device: {remote}', file=sys.stderr)
    else:
        print('XML dump skipped for privacy. Pass --include-xml to enable it deliberately.')
    print('Screenshots and XML may contain sensitive data; keep them out of Git.')


def compute_visual_diff(before_path: Path, after_path: Path, output: Path,
                        tolerance: int = 16, ignore_regions: list[tuple[int,int,int,int]] | None = None,
                        overwrite: bool = False) -> dict:
    try:
        from PIL import Image, ImageChops, ImageStat, ImageDraw
    except ImportError as ex:
        raise RuntimeError('Pillow is missing. Run pip install -r requirements.txt') from ex

    if not 0 <= tolerance <= 255:
        raise ValueError('Tolerance must be between 0 and 255.')
    inputs = {before_path.resolve(), after_path.resolve()}
    outputs = [output / name for name in ('difference.png', 'highlighted.png', 'comparison.json')]
    if any(path.resolve() in inputs or (path.exists() and any(path.samefile(source) for source in inputs)) for path in outputs):
        raise ValueError('The diff destination would overwrite an input image.')
    protect_outputs(outputs, overwrite)
    for region in ignore_regions or []:
        if len(region) != 4 or region[2] <= 0 or region[3] <= 0:
            raise ValueError('Ignored regions need a positive width and height.')
    with Image.open(before_path) as a, Image.open(after_path) as b:
        before=a.convert('RGB'); after=b.convert('RGB')
    report={'before':str(before_path.resolve()), 'after':str(after_path.resolve()),
            'size_before':list(before.size), 'size_after':list(after.size),
            'tolerance_channel':tolerance, 'ignored_rectangles':ignore_regions or [],
            'collected_utc':utc_now()}
    if before.size!=after.size:
        if overwrite and any(path.exists() for path in outputs[:2]):
            raise RuntimeError('Different dimensions; use a new destination so old results are not mixed.')
        report.update({'comparable':False,'reason':'Different dimensions. Capture at the same viewport and scale.'})
        dump_json(output/'comparison.json',report)
        return report

    diff=ImageChops.difference(before,after)
    w,h=before.size
    ignored = Image.new('L', (w, h), 0)
    ignored_draw = ImageDraw.Draw(ignored)
    for x,y,ww,hh in (ignore_regions or []):
        l,t,r,bot=max(0,x),max(0,y),min(w,x+ww),min(h,y+hh)
        if r>l and bot>t:
            diff.paste((0,0,0),(l,t,r,bot))
            ignored_draw.rectangle((l,t,r-1,bot-1), fill=255)
    ignored_pixels = ignored.histogram()[255]
    compared_pixels = w * h - ignored_pixels
    report.update({'ignored_pixels': ignored_pixels, 'compared_pixels': compared_pixels})
    if not compared_pixels:
        raise ValueError('Every area was ignored; there is nothing to compare.')
    r,g,b=diff.split()
    mask=ImageChops.lighter(ImageChops.lighter(r,g),b).point(lambda p: 255 if p>tolerance else 0)
    count=mask.histogram()[255]
    covered=mask.size[0]*mask.size[1]
    stat=ImageStat.Stat(diff)
    overlay=Image.blend(after, Image.new('RGB', after.size, (255,40,60)), 0.48)
    visual=after.copy(); visual.paste(overlay,(0,0),mask)
    output.mkdir(parents=True,exist_ok=True)
    diff.save(output/'difference.png')
    visual.save(output/'highlighted.png')
    report.update({'comparable':True, 'changed_pixels':count,
                   'changed_percent':round(count/covered*100,4),
                   'changed_percent_compared':round(count/compared_pixels*100,4),
                   'rms_per_channel': [round(v,4) for v in stat.rms],
                   'diff_png':str((output/'difference.png').resolve()),
                   'highlighted_png':str((output/'highlighted.png').resolve()),
                   'interpretation':'Objective pixel metric; not an aesthetic or UX score.'})
    dump_json(output/'comparison.json',report)
    return report


def parse_region(value: str) -> tuple[int,int,int,int]:
    parts=value.split(',')
    if len(parts)!=4:
        raise argparse.ArgumentTypeError('Use x,y,width,height')
    try: nums=tuple(int(x.strip()) for x in parts)
    except ValueError as ex:raise argparse.ArgumentTypeError('Four integers expected') from ex
    if nums[2]<=0 or nums[3]<=0:
        raise argparse.ArgumentTypeError('Width and height must be positive')
    return nums


def cmd_compare(args):
    if not (0<=args.tolerance<=255):raise ValueError('Tolerance must be between 0 and 255.')
    before=Path(args.before)
    after=Path(args.after)
    for path in [before,after]:
        if not path.is_file():raise RuntimeError(f'File not found: {path}')
    output=Path(args.output)
    report=compute_visual_diff(before,after,output,args.tolerance,args.ignore_region,args.overwrite)
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if not report['comparable']:
        return 2
    return 0


def cmd_test(args):
    flow=Path(args.flow).resolve()
    if not flow.is_file() or flow.suffix.lower() not in ('.yml','.yaml'):
        raise RuntimeError('Local YAML flow not found.')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+',args.app_id):
        raise ValueError('app-id must be a valid package ID (e.g. com.example.app).')
    if not shutil.which('maestro'):
        raise RuntimeError('Maestro CLI not found. See https://docs.maestro.dev')
    argv=['maestro']+(['--device',args.serial] if args.serial else [])+['test','-e',f'APP_ID={args.app_id}']
    if args.target_text:
        argv+=['-e',f'TARGET_TEXT={args.target_text}']
    argv.append(str(flow))
    print('Running Maestro flow LOCALLY, no cloud service...',flush=True)
    workdir = Path(args.workdir).resolve() if args.workdir else Path.cwd()
    if not workdir.is_dir():
        raise RuntimeError(f'Working directory not found: {workdir}')
    p=command(argv,timeout=args.timeout,cwd=workdir)
    if p.stdout: print(p.stdout)
    if p.stderr: print(p.stderr,file=sys.stderr)
    if p.returncode:
        raise RuntimeError(f'Maestro flow failed ({p.returncode})')
    print('Maestro flow passed (this is not aesthetic approval).')


def cmd_preview(args):
    if not shutil.which('scrcpy'):
        raise RuntimeError('scrcpy not found. Get it from the official Genymobile/scrcpy GitHub.')
    argv=['scrcpy']+(['--serial',args.serial] if args.serial else [])
    print('Opening LOCAL Android mirror (scrcpy). Close the window to finish.',flush=True)
    try:
        return subprocess.call(argv)
    except FileNotFoundError as ex:
        raise RuntimeError('scrcpy is not installed or not on PATH') from ex


def cmd_doctor(args):
    statuses={
        'python':sys.version.split()[0],
        'pillow': bool(importlib.util.find_spec('PIL')),
        'adb':shutil.which('adb'),
        'maestro':shutil.which('maestro'),
        'scrcpy_live_preview':shutil.which('scrcpy'),
        'java':shutil.which('java'),
        'npx_for_optional_impeccable':shutil.which('npx'),
    }
    print(json.dumps(statuses,indent=2,ensure_ascii=False))
    print('Note: finding a binary does NOT mean the app, emulator or any skill works.')


GUIDELINES_DIR = Path(__file__).resolve().parents[1] / 'data'
SEVERITY_RANK = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}


def filter_guidelines(stack: str, severity: str = 'low', category: str | None = None) -> list[dict]:
    path = GUIDELINES_DIR / f'{stack}.csv'
    if not path.is_file():
        raise ValueError(f'Unknown stack: {stack}')
    with path.open(encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh))
    floor = SEVERITY_RANK[severity]
    return [r for r in rows
            if SEVERITY_RANK.get(r.get('Severity', '').strip().lower(), 0) >= floor
            and (not category or category.lower() in r.get('Category', '').lower())]


def cmd_guidelines(args):
    rows = filter_guidelines(args.stack, args.severity, args.category)
    for r in rows:
        title = r.get('Guideline') or r.get('Issue')
        url = r.get('Docs URL') or ''
        avoid = r["Don't"]
        print(f"[{r['Severity']}] {r['Category']} — {title}\n  Do: {r['Do']}\n  Avoid: {avoid}" + (f'\n  {url}' if url else ''))
    print(f'{len(rows)} guideline(s) from data/{args.stack}.csv')


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as ex:
        raise argparse.ArgumentTypeError('Pass a positive integer.') from ex
    if number <= 0:
        raise argparse.ArgumentTypeError('Pass a positive integer.')
    return number


def parser():
    p=argparse.ArgumentParser(description='Local device tools: capture, inspect, compare, Maestro and guidelines')
    sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('doctor',help='Check local tooling');q.set_defaults(func=cmd_doctor)
    q=sub.add_parser('devices',help='List ADB devices');q.set_defaults(func=cmd_devices)
    q=sub.add_parser('capture',help='Capture PNG with adb')
    q.add_argument('--name',required=True);q.add_argument('--serial');q.add_argument('--output');q.add_argument('--overwrite',action='store_true');q.set_defaults(func=cmd_capture)
    q=sub.add_parser('inspect',help='Capture screen and optionally dump UI XML')
    q.add_argument('--name',required=True);q.add_argument('--serial');q.add_argument('--output-dir');q.add_argument('--include-xml',action='store_true');q.add_argument('--overwrite',action='store_true');q.set_defaults(func=cmd_inspect)
    q=sub.add_parser('compare',help='Compute offline pixel difference')
    q.add_argument('--before',required=True);q.add_argument('--after',required=True);q.add_argument('--output',required=True)
    q.add_argument('--tolerance',type=int,default=16);q.add_argument('--ignore-region',type=parse_region,action='append',default=[],help='x,y,width,height; repeatable')
    q.add_argument('--overwrite',action='store_true',help='Replace previous comparison outputs explicitly')
    q.set_defaults(func=cmd_compare)
    q=sub.add_parser('preview',help='Mirror Android screen live with optional scrcpy')
    q.add_argument('--serial');q.set_defaults(func=cmd_preview)
    q=sub.add_parser('test',help='Run Maestro flow LOCALLY')
    q.add_argument('--flow',required=True);q.add_argument('--app-id',required=True);q.add_argument('--target-text');q.add_argument('--serial')
    q.add_argument('--timeout',type=positive_int,default=240)
    q.add_argument('--workdir',help='Working directory for Maestro (default: current directory)');q.set_defaults(func=cmd_test)
    q=sub.add_parser('guidelines',help='Filter offline stack guidelines (references/data)')
    q.add_argument('--stack',required=True,choices=['compose','flutter','react-native','app-interface'])
    q.add_argument('--severity',choices=list(SEVERITY_RANK),default='high',help='Minimum severity (default: high)')
    q.add_argument('--category',help='Substring of the Category column, e.g. Accessibility');q.set_defaults(func=cmd_guidelines)
    return p


def main(argv=None):
    args=parser().parse_args(argv)
    try:
        return args.func(args) or 0
    except (RuntimeError,ValueError,PermissionError,OSError) as ex:
        print(f'ERROR: {ex}',file=sys.stderr)
        return 2

if __name__=='__main__':
    sys.exit(main())
