"""Evidence-led review for SANS 10142-1:2017 Edition 2.

A checklist is not a Certificate of Compliance or a determination of conformity.
"""
from datetime import datetime, timezone

REQUIREMENTS = (
    ('edition', 'Confirm applicable SANS edition and amendments', 'Scope and edition'),
    ('supply', 'Confirm AC/DC supply, nominal voltage, earthing arrangement and sources', '1.2, 6.11'),
    ('cable_method', 'Verify installation method, conductor material and cable construction', '6.2'),
    ('cable_tables', 'Verify source ampacity table and conductor size', '6.2, Tables 6.2-6.9'),
    ('corrections', 'Verify all applicable grouping, thermal, neutral and harmonic factors', '6.2, Tables 6.10-6.19'),
    ('voltage_drop', 'Verify complete circuit voltage drop and equipment requirements', '6.2.7'),
    ('overcurrent', 'Verify overcurrent protection for every required live conductor', '6.7.1'),
    ('breaking', 'Verify AC/DC device interrupting capacity at the installation point', '6.7.1'),
    ('fault_stress', 'Verify conductor and device thermal/short-circuit withstand', '6.7'),
    ('earthing', 'Verify protective conductor continuity, bonding and earth arrangement', '6.11-6.13'),
    ('fault_loop', 'Verify measured earth-fault-loop values and applicable criteria', '6.7, 8'),
    ('device_curve', 'Verify manufacturer time-current data and actual operating time', '6.7'),
    ('rcd', 'Verify applicable RCD selection, rating, function and test evidence', '5.2.3, 6.7'),
    ('dc_sources', 'For DC: verify each source has appropriate individual protection', '6.7.1.1'),
    ('dc_device', 'For DC: verify DC-rated protective device, polarity and arc interruption', '6.7'),
    ('inspection', 'Record inspection, instrument calibration and test evidence', '8'),
    ('signoff', 'Obtain required competent-person review and statutory documentation', '8'),
)
VALID_STATUSES = ('not checked', 'verified', 'issue', 'not applicable')


def review_evidence(records):
    """Report completeness and issues, never mark an installation compliant."""
    if not isinstance(records, dict):
        raise ValueError('Evidence must be a mapping')
    unknown = set(records) - {key for key, _, _ in REQUIREMENTS}
    if unknown:
        raise ValueError('Unknown requirement keys: ' + ', '.join(sorted(unknown)))
    rows = []
    for key, description, clause in REQUIREMENTS:
        item = records.get(key, {})
        if not isinstance(item, dict):
            raise ValueError(f'{key} must be an object')
        status = item.get('status', 'not checked')
        note = item.get('note', '')
        if status not in VALID_STATUSES or not isinstance(note, str) or len(note) > 2000:
            raise ValueError(f'Invalid evidence for {key}')
        if status in ('verified', 'not applicable') and not note.strip():
            raise ValueError(f'{key} requires a justification or evidence reference')
        rows.append({'key': key, 'description': description, 'clause': clause,
                     'status': status, 'note': note})
    counts = {s: sum(row['status'] == s for row in rows) for s in VALID_STATUSES}
    return {'reference': 'SANS 10142-1:2017 Edition 2 (verify applicability)',
            'generated_utc': datetime.now(timezone.utc).isoformat(),
            'items': rows, 'counts': counts,
            'outstanding': counts['not checked'] + counts['issue'],
            'compliance_status': 'NOT DETERMINED - professional verification required'}
