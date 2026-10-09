"""Video module for offline NPC training."""
import hashlib
import json
import shutil
import statistics
import subprocess
from pathlib import Path
from .common import number, read_csv
from .evaluation import split_sessions, diversity
from .styles import make_profiles

OBS_FIELDS = ('clip_id', 'track_id', 'confidence', 'pace_fraction', 'aggression',
              'corner_precision', 'lane_bias', 'decision_seconds')


def fit_observations(path, seed=42):
    rows = read_csv(path, OBS_FIELDS)
    groups = {}
    tracks = set()
    ranges = {'confidence': (.01, 1), 'pace_fraction': (0, 1), 'aggression': (0, 1),
              'corner_precision': (0, 1), 'lane_bias': (-1, 1), 'decision_seconds': (1.2, 3.5)}
    for line, row in enumerate(rows, 2):
        if not row['clip_id'].strip() or not row['track_id'].strip():
            raise ValueError(f'line {line}: clip_id/track_id required')
        values = {k: number(row[k], k, *limits) for k, limits in ranges.items()}
        groups.setdefault(row['clip_id'], []).append(values)
        tracks.add(row['track_id'])
    if len(tracks) != 1:
        raise ValueError('observations must describe one track')
    train, holdout = split_sessions(groups, seed)

    def aggregate(ids):
        # One vote per clip, preventing many annotations from dominating training.
        clips = []
        for clip in ids:
            observations = groups[clip]
            weight = sum(r['confidence'] for r in observations)
            clips.append({k: sum(r[k] * r['confidence'] for r in observations) / weight for k in ranges})
        return {k: round(statistics.mean(c[k] for c in clips), 6) for k in ranges}

    observed = aggregate(train)
    priors = {'aggression': .25 + observed['aggression'] * .72,
              'corner_skill': .95 + observed['corner_precision'] * .05,
              'preferred_lane_cm': observed['lane_bias'] * 45,
              'decision_seconds': observed['decision_seconds']}
    profiles = make_profiles(priors, seed)
    return {'schema_version': 1, 'track_id': next(iter(tracks)), 'seed': seed,
            'training': {'source': 'observations', 'input_sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                         'training_clips': len(train), 'holdout_clips': len(holdout),
                         'training_metrics': observed, 'holdout_metrics': aggregate(holdout),
                         'limits': 'Subjective manual annotations, not recovered steering or geometry. Pace is descriptive only.'},
            'profiles': profiles, 'diversity': diversity(profiles)}


def extract_frames(video, output, interval):
    executable = shutil.which('ffmpeg')
    if not executable:
        raise ValueError('FFmpeg not found on PATH; use an existing video player and manually annotate observations.csv')
    interval = number(interval, 'interval', .25, 60)
    video = Path(video).resolve()
    if not video.is_file():
        raise ValueError('video file does not exist')
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('frame directory already exists; choose a fresh directory to preserve files')
    output.mkdir(parents=True)
    subprocess.run([executable, '-nostdin', '-n', '-i', str(video), '-vf', f'fps=1/{interval},scale=1280:-2',
                    '-frames:v', '600', str(output / 'frame_%05d.jpg')], check=True)
    (output / 'provenance.json').write_text(json.dumps({'source_video': video.name,
        'sha256': hashlib.sha256(video.read_bytes()).hexdigest(), 'sample_interval_seconds': interval,
        'maximum_frames': 600, 'purpose': 'manual observations; no automatic driving policy inferred'}, indent=2), encoding='utf-8')
