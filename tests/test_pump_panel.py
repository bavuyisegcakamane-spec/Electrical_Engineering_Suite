#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

import pytest
from calculations.pump_panel import Pump, study_panel
from database.pump_panel_components import conceptual_bom


def test_four_45kw_pumps_exceed_150a_main():
    result = study_panel([Pump(45, 'VFD')] * 4)
    assert result['exceeds_main_rating']
    assert result['simultaneous_running_a'] > 150
    assert len(result['pumps']) == 4


def test_two_of_four_running_uses_largest_motors():
    result = study_panel([Pump(2.2), Pump(7.5), Pump(22), Pump(45)], simultaneous=2)
    expected = study_panel([Pump(22), Pump(45)])
    assert result['simultaneous_running_a'] == expected['simultaneous_running_a']
    assert result['installed_running_a'] > result['simultaneous_running_a']


def test_starter_does_not_change_running_motor_current():
    currents = [study_panel([Pump(11, starter)])['simultaneous_running_a']
                for starter in ('DOL','Star-delta','Soft starter','VFD')]
    assert len(set(currents)) == 1


@pytest.mark.parametrize('pumps,simultaneous', [([],None), ([Pump(2.2)] * 5,None),
    ([Pump(1)],None), ([Pump(46)],None), ([Pump(7.5)],2)])
def test_reject_invalid_inputs(pumps,simultaneous):
    with pytest.raises(ValueError):
        study_panel(pumps, simultaneous=simultaneous)


def test_bom_has_branch_specific_components():
    bom = conceptual_bom(['DOL','Star-delta','Soft starter','VFD'])
    assert len(bom['per_pump']) == 4
    assert 'Main circuit breaker' in bom['common']
    assert any('Six-lead' in x for x in bom['per_pump'][1]['components'])
    assert any('drive' in x.lower() for x in bom['per_pump'][3]['components'])
