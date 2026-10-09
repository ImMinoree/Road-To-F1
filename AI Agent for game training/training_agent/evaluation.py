"""Evaluation module for offline NPC training."""
import math
import random
import statistics
from .common import BOUNDS

def split_sessions(sessions, seed):
    if len(sessions) < 2:
        raise ValueError('at least two distinct sessions required for a session-level holdout')
    ordered = sorted(sessions)
    random.Random(seed).shuffle(ordered)
    count = max(1, round(len(ordered) * .25))
    holdout = ordered[:count]
    train = ordered[count:]
    return train, holdout


def diversity(profiles):
    normalized = [[(p[key] - lo) / (hi - lo) for key, (lo, hi) in BOUNDS.items()] for p in profiles]
    distances = [math.dist(a, b) for i, a in enumerate(normalized) for b in normalized[i + 1:]]
    return {'unique_profiles': len({tuple(p[k] for k in BOUNDS) for p in profiles}),
            'minimum_normalized_distance': round(min(distances), 6),
            'mean_normalized_distance': round(statistics.mean(distances), 6),
            'parameter_ranges': {key: [min(p[key] for p in profiles), max(p[key] for p in profiles)] for key in BOUNDS},
            'interpretation': 'Parameter diversity only; does not prove varied or safe on-track behaviour.'}
