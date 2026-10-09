"""Learning module for offline NPC training."""
import hashlib
import statistics
from pathlib import Path
from .common import clamp
from .telemetry import load_telemetry
from .evaluation import split_sessions, diversity
from .styles import make_profiles

def summary(records):
    """Time-weighted session summaries; equal session weights resist long-run dominance."""
    totals = []
    for record in records:
        samples = record['samples']
        duration = samples[-1]['time_seconds'] - samples[0]['time_seconds']
        clean = [(a, b) for a, b in zip(samples, samples[1:])
                 if a['speed_kmh'] >= 0 and b['speed_kmh'] >= 0 and a['throttle'] >= 0
                 and b['throttle'] >= 0 and not a['burning'] and not b['burning']]
        clean_duration = sum(b['time_seconds'] - a['time_seconds'] for a, b in clean)
        if clean_duration < 1:
            raise ValueError('each session needs at least one second of forward, non-burning movement for skill summaries')
        values = {'pace': 0, 'throttle': 0, 'steering_activity': 0, 'lane_bias': 0,
                  'burning_fraction': 0, 'reverse_fraction': 0, 'clean_fraction': clean_duration / duration}
        for previous, sample in zip(samples, samples[1:]):
            dt = sample['time_seconds'] - previous['time_seconds']
            values['burning_fraction'] += previous['burning'] * dt / duration
            values['reverse_fraction'] += int(previous['speed_kmh'] < 0 or previous['throttle'] < 0) * dt / duration
        for previous, sample in clean:
            dt = sample['time_seconds'] - previous['time_seconds']
            for key, value in [('pace', previous['speed_kmh'] / 57), ('throttle', previous['throttle']),
                               ('lane_bias', previous['lane_cm'] / 130)]:
                values[key] += clamp(value, -1 if key == 'lane_bias' else 0, 1) * dt / clean_duration
            values['steering_activity'] += abs(sample['steering'] - previous['steering']) / clean_duration
        values['collisions_per_minute'] = (samples[-1]['collision_count'] - samples[0]['collision_count']) * 60 / duration
        totals.append(values)
    return {key: round(statistics.mean(v[key] for v in totals), 6) for key in totals[0]}


def tendencies(metrics):
    # Descriptive pace and smoothness proxies, NOT claims about optimum racing technique.
    incident = clamp(metrics['collisions_per_minute'] / 3 + metrics['burning_fraction'], 0, 1)
    return {'aggression': clamp(.35 + .4 * metrics['pace'] + .1 * metrics['throttle'] - .3 * incident, .25, .97),
            'corner_skill': clamp(.997 - .02 * clamp(metrics['steering_activity'], 0, 1) - .02 * incident, .95, 1),
            'preferred_lane_cm': clamp(metrics['lane_bias'] * 45, -45, 45),
            'decision_seconds': clamp(2.4 + .5 * incident + .3 * clamp(metrics['steering_activity'], 0, 1), 1.2, 3.5)}


def contexts(records):
    """Context-conditioned aggregates require recorder-derived geometry/traffic fields."""
    buckets = {key: [] for key in ('corner', 'straight', 'near_traffic', 'closing_traffic')}
    for record in records:
        per_session = {key: [] for key in buckets}
        for previous, sample in zip(record['samples'], record['samples'][1:]):
            if (previous['speed_kmh'] < 0 or sample['speed_kmh'] < 0 or previous['throttle'] < 0
                    or sample['throttle'] < 0 or previous['burning'] or sample['burning']):
                continue
            dt = sample['time_seconds'] - previous['time_seconds']
            labels = []
            if 'curvature' in previous:
                labels.append('corner' if previous['curvature'] >= .0002 else 'straight')
            if previous.get('nearest_ahead_cm', 100001) <= 800:
                labels.append('near_traffic')
                if previous.get('relative_speed_kmh', 0) > 0:
                    labels.append('closing_traffic')
            for label in labels:
                per_session[label].append((dt, previous['speed_kmh'], previous['brake'], abs(previous['steering'])))
        for label, samples in per_session.items():
            duration = sum(s[0] for s in samples)
            if duration >= 1:
                buckets[label].append({'seconds': duration,
                    'mean_speed_kmh': sum(s[0] * s[1] for s in samples) / duration,
                    'brake_fraction': sum(s[0] * s[2] for s in samples) / duration,
                    'mean_absolute_steering': sum(s[0] * s[3] for s in samples) / duration})
    return {label: {'sessions_with_coverage': len(samples),
                   'observed_seconds': round(sum(s['seconds'] for s in samples), 3),
                   **{key: round(statistics.mean(s[key] for s in samples), 6)
                      for key in ('mean_speed_kmh', 'brake_fraction', 'mean_absolute_steering')}}
            for label, samples in buckets.items() if samples}


def fit_telemetry(path, seed=42, source='telemetry'):
    sessions = load_telemetry(path)
    tracks = {r['track_id'] for r in sessions.values()}
    if len(tracks) != 1:
        raise ValueError('train each track separately; input contains multiple tracks')
    train_ids, holdout_ids = split_sessions(sessions, seed)
    training = summary([sessions[i] for i in train_ids])
    holdout = summary([sessions[i] for i in holdout_ids])
    context_metrics = contexts([sessions[i] for i in train_ids])
    priors = tendencies(training)
    # Small safety-biased adjustment from observed traffic braking. Corner speed is
    # reported, not blindly copied: faster recorded corners need not be safe.
    traffic = context_metrics.get('closing_traffic', {})
    if traffic.get('sessions_with_coverage', 0) >= 2:
        priors['aggression'] = clamp(priors['aggression'] - .05 * traffic['brake_fraction'], .25, .97)
    profiles = make_profiles(priors, seed)
    # Counts and aggregate gaps only: no session IDs or recorded sequences in export.
    return {'schema_version': 1, 'track_id': next(iter(tracks)), 'seed': seed,
            'training': {'source': source, 'input_sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                         'method': 'bounded aggregate tendency fitting; independent stratified personalities',
                         'training_sessions': len(train_ids), 'holdout_sessions': len(holdout_ids),
                         'training_metrics': training, 'holdout_metrics': holdout,
                         'context_metrics': context_metrics,
                         'holdout_context_metrics': contexts([sessions[i] for i in holdout_ids]),
                         'context_limits': 'Observed braking/pace correlations only; not causal skill labels or overtaking success predictions.',
                         'holdout_absolute_gaps': {k: round(abs(training[k] - holdout[k]), 6) for k in training},
                         'validation': 'session holdout descriptive agreement only; Unreal race tests still required'},
            'profiles': profiles, 'diversity': diversity(profiles)}
