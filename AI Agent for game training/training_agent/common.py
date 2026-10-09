"""Common module for offline NPC training."""
import csv
import math
from pathlib import Path

FIELDS = ('time_seconds', 'session_id', 'track_id', 'route_index', 'lane_cm',
          'speed_kmh', 'throttle', 'steering', 'brake', 'collision_count', 'burning')


BOUNDS = {'aggression': (.25, .97), 'corner_skill': (.95, 1.0),
          'preferred_lane_cm': (-130, 130), 'decision_seconds': (1.2, 3.5)}


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def number(value, field, lo=None, hi=None):
    try:
        n = float(value)
    except (ValueError, TypeError):
        raise ValueError(f'{field}: expected a number') from None
    if not math.isfinite(n) or (lo is not None and n < lo) or (hi is not None and n > hi):
        raise ValueError(f'{field}: nonfinite or outside [{lo}, {hi}]')
    return n


def integer(value, field):
    n = number(value, field, 0)
    if n != int(n):
        raise ValueError(f'{field}: expected a nonnegative integer')
    return int(n)


def read_csv(path, required):
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(required) <= set(reader.fieldnames):
            raise ValueError('missing columns: ' + ', '.join(sorted(set(required) - set(reader.fieldnames or []))))
        rows = list(reader)
    if not rows:
        raise ValueError('input is empty')
    return rows
