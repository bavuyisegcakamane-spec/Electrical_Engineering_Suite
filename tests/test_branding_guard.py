#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Verify the source-branding guard, including safe shebang handling."""
import tempfile
from pathlib import Path
from tools.branding_guard import MARKER, add_banner, run


def test_banner_preserves_shebang_and_coding():
    source = '#!/usr/bin/env python3\n# coding: utf-8\nprint(1)\n'
    result = add_banner(source)
    assert result.startswith('#!/usr/bin/env python3\n# coding: utf-8\n')
    assert MARKER in result
    assert result.endswith('print(1)\n')
    assert add_banner(result) == result


def test_missing_brand_fails_then_fixes():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'sample.py'
        path.write_text('x = 1\n', encoding='utf-8')
        assert run(paths=[path]) == 1
        assert run(fix=True, paths=[path]) == 0
        assert run(paths=[path]) == 0
        assert MARKER in path.read_text(encoding='utf-8')
