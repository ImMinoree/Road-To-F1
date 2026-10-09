import csv
import json
from pathlib import Path
import tempfile
import unittest
import train


class TrainingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='.test-', dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'demo.csv'
        train.write_demo(self.path)

    def mutate(self, edit):
        rows = train.read_csv(self.path, train.FIELDS)
        edit(rows)
        with self.path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def test_deterministic_distinct_bounded_profiles(self):
        first = train.fit_telemetry(self.path)
        self.assertEqual(first, train.fit_telemetry(self.path))
        self.assertNotEqual(first['profiles'], train.fit_telemetry(self.path, 43)['profiles'])
        self.assertEqual([p['racer_index'] for p in first['profiles']], list(range(1, 20)))
        self.assertEqual(first['diversity']['unique_profiles'], 19)
        self.assertGreater(first['diversity']['minimum_normalized_distance'], .02)
        for profile in first['profiles']:
            for key, (lo, hi) in train.BOUNDS.items():
                self.assertGreaterEqual(profile[key], lo)
                self.assertLessEqual(profile[key], hi)

    def test_invalid_finite_controls_and_headers(self):
        for value in ('nan', 'inf', '1.01', '-1.01', 'abc'):
            train.write_demo(self.path)
            self.mutate(lambda rows: rows[0].update(throttle=value))
            with self.assertRaises(ValueError):
                train.load_telemetry(self.path)
        self.path.write_text('speed_kmh\n10\n')
        with self.assertRaisesRegex(ValueError, 'missing columns'):
            train.load_telemetry(self.path)

    def test_restart_and_order_validation(self):
        for field, value in [('time_seconds', '0'), ('collision_count', '-1'), ('route_index', '1.5'), ('burning', '2')]:
            train.write_demo(self.path)
            self.mutate(lambda rows: rows[1].update({field: value}))
            with self.assertRaises(ValueError):
                train.load_telemetry(self.path)
        train.write_demo(self.path)
        self.mutate(lambda rows: (rows[0].update(collision_count='1'), rows[1].update(collision_count='0')))
        with self.assertRaisesRegex(ValueError, 'decreased'):
            train.load_telemetry(self.path)

    def test_holdout_sessions_do_not_change_profiles(self):
        sessions = train.load_telemetry(self.path)
        trained, held = train.split_sessions(sessions, 42)
        self.assertFalse(set(trained) & set(held))
        first = train.fit_telemetry(self.path)
        self.mutate(lambda rows: [row.update(speed_kmh='0', throttle='0', steering='1')
                                 for row in rows if row['session_id'] in held])
        changed = train.fit_telemetry(self.path)
        self.assertEqual(first['profiles'], changed['profiles'])
        self.assertEqual(first['training']['training_metrics'], changed['training']['training_metrics'])
        self.assertNotEqual(first['training']['holdout_metrics'], changed['training']['holdout_metrics'])

    def test_track_isolation_and_minimum_sessions(self):
        self.mutate(lambda rows: [row.update(track_id='OTHER') for row in rows if row['session_id'] == 'SYNTHETIC_DEMO_3'])
        with self.assertRaisesRegex(ValueError, 'multiple tracks'):
            train.fit_telemetry(self.path)
        train.write_demo(self.path)
        rows = train.read_csv(self.path, train.FIELDS)[:121]
        with self.path.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=train.FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaisesRegex(ValueError, 'two distinct'):
            train.fit_telemetry(self.path)

    def test_no_trajectory_or_control_replay_export(self):
        result = train.fit_telemetry(self.path)
        encoded = json.dumps(result)
        for forbidden in ('SYNTHETIC_DEMO_0', 'time_seconds', 'route_index', 'samples', 'session_id'):
            self.assertNotIn(forbidden, encoded)
        for profile in result['profiles']:
            self.assertEqual(set(profile), {'racer_index', *train.BOUNDS})

    def test_context_statistics_and_holdout_isolation(self):
        def add_context(rows):
            for row in rows:
                row.update(curvature='.002' if int(float(row['time_seconds'])) % 2 else '0',
                           nearest_ahead_cm='400', relative_speed_kmh='10',
                           next_checkpoint='2', completed_laps='0')
        self.mutate(add_context)
        result = train.fit_telemetry(self.path)
        self.assertEqual(set(result['training']['context_metrics']), {'corner', 'straight', 'near_traffic', 'closing_traffic'})
        self.assertEqual(result['training']['context_metrics']['closing_traffic']['sessions_with_coverage'], 3)
        self.assertNotIn('curvature', json.dumps(result['profiles']))

    def test_observation_validation_and_clip_holdout(self):
        observation = Path(self.temp.name) / 'observations.csv'
        with observation.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=train.OBS_FIELDS)
            writer.writeheader()
            for i in range(4):
                writer.writerow(dict(zip(train.OBS_FIELDS, [f'clip{i}', 'SouthGarda_KartRace', .7, .6, .4, .8, 0, 2.4])))
        result = train.fit_observations(observation)
        self.assertEqual(result['training']['training_clips'], 3)
        self.assertEqual(result['training']['holdout_clips'], 1)
        self.assertEqual(result['diversity']['unique_profiles'], 19)
        self.assertEqual(result, train.fit_observations(observation))
        observation.write_text(observation.read_text().replace('0.7', 'nan'))
        with self.assertRaises(ValueError):
            train.fit_observations(observation)

    def test_missing_video_executable_is_actionable(self):
        from unittest.mock import patch
        with patch('training_agent.video.shutil.which', return_value=None):
            with self.assertRaisesRegex(ValueError, 'manually annotate'):
                train.extract_frames('missing.mp4', Path(self.temp.name) / 'frames', 2)

    def test_reverse_is_accepted_but_excluded_from_skill(self):
        def reverse(rows):
            for row in rows:
                if float(row['time_seconds']) < 10:
                    row.update(speed_kmh='-14.4', throttle='-1', lane_cm='9999', steering='1')
        self.mutate(reverse)
        sessions = train.load_telemetry(self.path)
        report = train.summary(list(sessions.values()))
        self.assertGreater(report['reverse_fraction'], 0)
        self.assertLess(report['pace'], 1)
        self.assertLess(abs(report['lane_bias']), .2)
        self.assertEqual(len(train.fit_telemetry(self.path)['profiles']), 19)

    def test_reverse_only_session_has_no_skill_data(self):
        self.mutate(lambda rows: [r.update(speed_kmh='-10', throttle='-1') for r in rows])
        train.load_telemetry(self.path)
        with self.assertRaisesRegex(ValueError, 'forward'):
            train.fit_telemetry(self.path)


if __name__ == '__main__':
    unittest.main()
