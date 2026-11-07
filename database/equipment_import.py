#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Import source-traceable equipment rows from locally reviewed CSV exports.

This does not scrape websites or verify manufacturer claims automatically.
"""
import csv
import io
import json
from datetime import datetime
from database.equipment_catalog import _source

COLUMNS = ('manufacturer','model','category','description','source_url','source_type',
           'source_checked_utc','specifications_json')


def parse_equipment_csv(content):
    if not isinstance(content, str) or len(content) > 2_000_000:
        raise ValueError('CSV must be text under 2 MB')
    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames != list(COLUMNS):
        raise ValueError('CSV header must match the documented equipment import template')
    records = []
    for row in reader:
        if len(records) >= 1000:
            raise ValueError('Maximum 1000 records per import')
        if None in row or any(not isinstance(row[k],str) or not row[k].strip() for k in COLUMNS):
            raise ValueError('Missing required CSV value')
        for k in COLUMNS[:6]:
            if len(row[k]) > 5000:
                raise ValueError('Equipment text field too long')
        _source(row['source_url'])
        try:
            checked = datetime.fromisoformat(row['source_checked_utc'].replace('Z','+00:00'))
            if checked.tzinfo is None:
                raise ValueError('Timestamp needs timezone')
            specs = json.loads(row['specifications_json'])
            if not isinstance(specs,dict) or any(not isinstance(k,str) or not isinstance(v,(str,int,float,bool,type(None))) for k,v in specs.items()):
                raise ValueError('Specifications must be flat JSON object')
            json.dumps(specs,allow_nan=False)
        except (ValueError,TypeError) as exc:
            raise ValueError('Invalid timestamp or specifications JSON') from exc
        records.append((row,specs))
    if not records:
        raise ValueError('CSV contains no equipment')
    return records


def import_equipment_csv(catalog,content):
    records = parse_equipment_csv(content)
    connection = catalog.db.connection
    # Atomic import: no partial records if any row is invalid or insert fails.
    with connection:
        for row,specs in records:
            connection.execute('''INSERT INTO equipment_catalog
                (manufacturer,model,category,description,source_url,source_type,verified_utc,captured_utc,specifications_json)
                VALUES (?,?,?,?,?,?,?,?,?)
                ON CONFLICT(manufacturer,model,source_url) DO NOTHING''',
                (row['manufacturer'].strip(),row['model'].strip(),row['category'].strip(),
                 row['description'].strip(),row['source_url'],row['source_type'],
                 row['source_checked_utc'],datetime.now().astimezone().isoformat(),
                 json.dumps(specs,allow_nan=False)))
    return len(records)
