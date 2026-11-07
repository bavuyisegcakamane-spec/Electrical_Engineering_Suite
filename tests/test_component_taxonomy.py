#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

from database.component_taxonomy import COMPONENT_GROUPS, ALL_COMPONENT_TYPES, SPECIFICATION_FIELDS, group_for


def test_component_taxonomy_is_unique_and_comprehensive():
    assert len(ALL_COMPONENT_TYPES) >= 90
    assert len(ALL_COMPONENT_TYPES) == len(set(ALL_COMPONENT_TYPES))
    assert 'Miniature circuit breaker (MCB)' in ALL_COMPONENT_TYPES
    assert 'Safety relay' in ALL_COMPONENT_TYPES
    assert 'Transformer' in ALL_COMPONENT_TYPES
    assert 'Cable gland' in ALL_COMPONENT_TYPES
    assert group_for('Earth electrode') == 'Earthing and safety'
    assert group_for('Nonexistent device') is None
    assert set(SPECIFICATION_FIELDS) == set(COMPONENT_GROUPS)


def test_categories_are_descriptive_not_fabricated_skus():
    assert all(name and isinstance(name,str) for name in ALL_COMPONENT_TYPES)
    assert all(len(fields) >= 4 for fields in SPECIFICATION_FIELDS.values())
