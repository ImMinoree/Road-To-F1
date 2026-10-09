"""Telemetry module for offline NPC training."""
import csv
import math
import random
from pathlib import Path
from .common import FIELDS, number, integer, read_csv

def load_telemetry(path):
    sessions = {}
    for line, row in enumerate(read_csv(path, FIELDS), 2):
        try:
            session = row['session_id'].strip()
            track = row['track_id'].strip()
            if not session or not track:
                raise ValueError('session_id and track_id must be nonempty')
            sample = {'time_seconds': number(row['time_seconds'], 'time_seconds', 0),
                      'route_index': integer(row['route_index'], 'route_index'),
                      'lane_cm': number(row['lane_cm'], 'lane_cm', -10000, 10000),
                      'speed_kmh': number(row['speed_kmh'], 'speed_kmh', -250, 250),
                      'throttle': number(row['throttle'], 'throttle', -1, 1),
                      'steering': number(row['steering'], 'steering', -1, 1),
                      'brake': number(row['brake'], 'brake', 0, 1),
                      'collision_count': integer(row['collision_count'], 'collision_count'),
                      'burning': integer(row['burning'], 'burning')}
            if sample['burning'] > 1:
                raise ValueError('burning must be 0 or 1')
            for key, limits in {'curvature': (0, 1), 'nearest_ahead_cm': (0, 100000),
                                'relative_speed_kmh': (-250, 250)}.items():
                if row.get(key, '').strip():
                    sample[key] = number(row[key], key, *limits)
            for key in ('next_checkpoint', 'completed_laps'):
                if row.get(key, '').strip():
                    sample[key] = integer(row[key], key)
            record = sessions.setdefault(session, {'track_id': track, 'samples': []})
            if record['track_id'] != track:
                raise ValueError('a session cannot change track')
            if record['samples']:
                prev = record['samples'][-1]
                if sample['time_seconds'] <= prev['time_seconds']:
                    raise ValueError('time must strictly increase within each session; restart needs a new session_id')
                if sample['collision_count'] < prev['collision_count']:
                    raise ValueError('collision_count decreased; restart needs a new session_id')
            record['samples'].append(sample)
        except (ValueError, AttributeError) as error:
            raise ValueError(f'CSV line {line}: {error}') from None
    for session, record in sessions.items():
        if len(record['samples']) < 3 or record['samples'][-1]['time_seconds'] - record['samples'][0]['time_seconds'] < 1:
            raise ValueError(f'session {session}: at least three samples and one second required')
    return sessions


def write_demo(path):
    rng = random.Random(17)
    with Path(path).open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for session in range(4):
            for tick in range(121):
                writer.writerow(dict(zip(FIELDS, [tick * .5, f'SYNTHETIC_DEMO_{session}', 'SouthGarda_KartRace',
                    tick % 60, round(math.sin(tick / 10 + session) * 80, 3),
                    round(30 + session * 2 + math.sin(tick / 8) * 8, 3),
                    round(rng.uniform(.5, 1), 4), round(math.sin(tick / 11) * .35, 4),
                    int(tick % 23 == 0), 0, 0])))
