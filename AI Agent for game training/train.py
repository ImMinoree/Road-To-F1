"""RoadToF1 offline training CLI; public re-exports preserve scripts/tests."""
import argparse
import json
from pathlib import Path
import subprocess
from training_agent.common import FIELDS, BOUNDS, clamp, number, integer, read_csv
from training_agent.telemetry import load_telemetry, write_demo
from training_agent.evaluation import split_sessions, diversity
from training_agent.learning import summary, tendencies, contexts, fit_telemetry
from training_agent.styles import make_profiles
from training_agent.video import OBS_FIELDS, fit_observations, extract_frames

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('telemetry', 'observations'):
        command = commands.add_parser(name)
        command.add_argument('input', type=Path)
        command.add_argument('--output', required=True, type=Path)
        command.add_argument('--seed', type=int, default=42)
    demo = commands.add_parser('demo')
    demo.add_argument('--directory', required=True, type=Path)
    frames = commands.add_parser('frames')
    frames.add_argument('video', type=Path)
    frames.add_argument('--directory', required=True, type=Path)
    frames.add_argument('--interval', type=float, default=2)
    args = parser.parse_args()
    try:
        if args.command == 'frames':
            extract_frames(args.video, args.directory, args.interval)
        elif args.command == 'demo':
            if args.directory.exists():
                raise ValueError('demo directory already exists; choose a fresh directory')
            args.directory.mkdir(parents=True)
            path = args.directory / 'SYNTHETIC_telemetry.csv'
            write_demo(path)
            (args.directory / 'SYNTHETIC_profiles.json').write_text(json.dumps(fit_telemetry(path, source='synthetic_demo'), indent=2), encoding='utf-8')
            print('Synthetic demonstration only. No real driver data was learned.')
        else:
            if args.output.exists():
                raise ValueError('output exists; choose a new output filename')
            result = fit_telemetry(args.input, args.seed) if args.command == 'telemetry' else fit_observations(args.input, args.seed)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')
            print(f'Generated 19 distinct bounded profiles in {args.output}; validate in Unreal before deployment.')
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(2, f'error: {error}\n')


if __name__ == '__main__':
    main()
