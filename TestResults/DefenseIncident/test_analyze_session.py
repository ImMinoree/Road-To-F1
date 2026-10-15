"""Run with Python: test_analyze_session.py. Evaluation labels are heuristic."""
import csv,json,subprocess,sys,unittest
from pathlib import Path

class EvaluationTest(unittest.TestCase):
 def analyze(self,changes):
  fields='schema time player_position player_contacts npc defends rival ahead_cm distance_cm contacts speed_kmh defend defense_outcome burning incident repass_attempts repass_completed'.split()
  base=dict.fromkeys(fields,'0');base.update(schema='2',npc='1',distance_cm='500',speed_kmh='50')
  rows=[]
  for values in changes:
   row=base.copy();row.update({k:str(v) for k,v in values.items()});rows.append(row)
  # Local fixture outputs never touch or train from human telemetry.
  d=Path(__file__).parent/'AnalyzerFixtures';d.mkdir(exist_ok=True)
  p=d/(self._testMethodName+'.csv')
  with p.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
  return json.loads(subprocess.check_output([sys.executable,str(Path(__file__).with_name('analyze_session.py')),str(p)]))
 def test_crossing_consumed_once(self):
  out=self.analyze([dict(time=0,player_position=20,ahead_cm=-200),dict(time=.2,player_position=19,ahead_cm=200),dict(time=.4,player_position=18,ahead_cm=220)])
  self.assertEqual(out['labels'],{'CLEAN_OVERTAKE':1,'UNKNOWN':1})
 def test_slow_flag_is_not_crash_proof(self):
  out=self.analyze([dict(time=0,player_position=20,ahead_cm=-200,speed_kmh=10,incident=1),dict(time=.2,player_position=19,ahead_cm=200,speed_kmh=10,incident=1)])
  self.assertEqual(out['labels'],{'AI_STOPPED_OR_SLOWED':1})
 def test_contact_context_is_heuristic(self):
  out=self.analyze([dict(time=0,player_position=20,ahead_cm=-200),dict(time=.2,player_position=19,ahead_cm=200,player_contacts=1)])
  self.assertEqual(out['labels'],{'CONTACT_GAIN':1})
 def test_stale_defense_outcome_not_reused(self):
  out=self.analyze([dict(time=0,player_position=20,ahead_cm=-200,defense_outcome=2),dict(time=.2,player_position=19,ahead_cm=200,defense_outcome=2)])
  self.assertEqual(out['labels'],{'CLEAN_OVERTAKE':1})
if __name__=='__main__':unittest.main()
