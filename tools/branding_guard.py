#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Check or add raw.bytes attribution to first-party Python source files.

python tools/branding_guard.py --check
python tools/branding_guard.py --fix
"""
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = '# Developer signature: raw.bytes. Third-party rights remain with their owners.'
BANNER = (
    '#  ____      ___        __  ____   _______ _____ ____\n'
    '# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|\n'
    '# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\\n'
    '# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |\n'
    '# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/\n'
    '#              . bytes  |  raw.bytes  |  (c) 2026\n'
    + MARKER + '\n'
)


def first_party_files():
    output = subprocess.check_output(['git', 'ls-files', '--cached', '--others',
                                      '--exclude-standard', '-z', '--', '*.py'], cwd=ROOT)
    paths = []
    for name in output.decode('utf-8', 'surrogateescape').split('\0'):
        if not name:
            continue
        path = ROOT / name
        if path.is_file() and not any(part in ('vendor', 'third_party', '.venv', 'venv', 'site-packages')
                                      for part in path.relative_to(ROOT).parts):
            paths.append(path)
    return paths


def add_banner(content):
    if any(line == MARKER for line in content.splitlines()[:15]):
        return content
    lines = content.splitlines(keepends=True)
    position = 1 if lines and lines[0].startswith('#!') else 0
    if position < len(lines) and ('coding:' in lines[position] or 'coding=' in lines[position]):
        position += 1
    newline = '\r\n' if '\r\n' in content else '\n'
    return ''.join(lines[:position]) + BANNER.replace('\n', newline) + newline + ''.join(lines[position:])


def run(fix=False, paths=None):
    missing = []
    for path in paths if paths is not None else first_party_files():
        content = path.read_text(encoding='utf-8-sig')
        if not any(line == MARKER for line in content.splitlines()[:15]):
            missing.append(path)
            if fix:
                with path.open('w', encoding='utf-8', newline='') as stream:
                    stream.write(add_banner(content))
    for path in missing:
        print(('BRANDED' if fix else 'MISSING') + ': ' + str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path))
    print(f'{len(missing)} files {"branded" if fix else "missing branding"}.')
    return 0 if fix or not missing else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--fix', action='store_true')
    args = parser.parse_args()
    raise SystemExit(run(fix=args.fix))
