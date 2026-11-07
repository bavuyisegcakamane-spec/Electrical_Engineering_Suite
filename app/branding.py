#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Internal application attribution metadata.

The signature is embedded in source as Unicode escapes to avoid encoding issues.
This is attribution metadata, not copy protection or a legal ownership claim
on third-party code, manufacturer data, or standards.
"""
DEVELOPER_BRAND = 'raw.bytes'
BRAND_YEAR = 2026
# Deliberately stored as escaped code points rather than a visible banner.
BRAND_SIGNATURE = '\u27e6 raw.bytes \u00a9 2026 \u27e7'
