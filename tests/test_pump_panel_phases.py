"""Single-phase pump panels and existing-database migration tests."""
import tempfile
from math import sqrt
from pathlib import Path

import pytest
from calculations.pump_panel import Pump, study_panel
from database.database import Database
from database.pump_panel_database import PumpPanelDatabase


def test_single_phase_panel_current_and_restricted_starter():
    result = study_panel([Pump(2.2)], voltage_v=220, phases=1)
    assert result['phases'] == 1
    assert result['simultaneous_running_a'] == pytest.approx(
        round(2200 / (220 * .85 * .90), 2))
    with pytest.raises(ValueError):
        study_panel([Pump(2.2, 'Star-delta')], voltage_v=220, phases=1)


def test_default_three_phase_unchanged():
    result = study_panel([Pump(2.2)], voltage_v=400)
    assert result['phases'] == 3
    assert result['simultaneous_running_a'] == pytest.approx(
        round(2200 / (sqrt(3) * 400 * .85 * .90), 2))


def test_existing_saved_panel_migrates_to_three_phase():
    with tempfile.TemporaryDirectory() as folder:
        db = Database(Path(folder) / 'panel.db')
        db.initialize()
        try:
            repo = PumpPanelDatabase(db)
            old_id = repo.create_panel('Existing', [Pump(2.2)])
            db.connection.execute('UPDATE pump_panel_designs SET phases=3 WHERE id=?', (old_id,))
            new_id = repo.create_panel('Single phase', [Pump(2.2)],
                                       voltage_v=220, phases=1)
            panels = {p['id']: p for p in repo.list_panels()}
            assert panels[old_id]['phases'] == 3
            assert panels[new_id]['phases'] == 1
            single_bom = repo.get_bom(new_id)
            assert single_bom  # Limited review-only single-phase checklist
            assert any(r['component'] == 'Site short-circuit study' for r in single_bom)
            assert not any('Phase loss' in r['component'] for r in single_bom)
            assert len(repo.get_bom(old_id)) > 0
        finally:
            db.close()


@pytest.mark.parametrize('phases', [0, 2, True, 1.0, None])
def test_invalid_phases(phases):
    with pytest.raises(ValueError):
        study_panel([Pump(2.2)], phases=phases)
