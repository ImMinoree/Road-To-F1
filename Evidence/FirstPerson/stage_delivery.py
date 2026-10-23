"""Stage this delivery without including unrelated edits to the shared pawn files."""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def git(*args, data=None):
    return subprocess.check_output(['git',*args],cwd=ROOT,input=data)
assert not git('diff','--cached','--name-only').strip(), 'Existing staged changes; inspect before proceeding'
for name in ['ProofPawn.cpp','ProofPawn.h']:
    path='Source/Road_To_F1_New/'+name
    base=git('show','HEAD:'+path).decode()
    if name.endswith('.cpp'):
        base=base.replace('#include "ProofPawn.h"','#include "ProofPawn.h"\n#include "LocalKartDriverVisuals.h"',1)
        anchor=' AutoPossessPlayer=EAutoReceiveInput::Player0;'
        assert anchor in base
        base=base.replace(anchor,' LocalDriverVisuals=CreateDefaultSubobject<ULocalKartDriverVisuals>(TEXT("LocalDriverVisuals"));\n'+anchor,1)
        anchor=' Speed=FMath::Clamp('
        assert anchor in base
        base=base.replace(anchor,' LocalDriverVisuals->SetSteeringInput(Steer);\n'+anchor,1)
    else:
        base=base.replace('class USphereComponent;','class USphereComponent;\nclass ULocalKartDriverVisuals;',1)
        anchor=' UPROPERTY() UCameraComponent* Camera;'
        assert anchor in base
        base=base.replace(anchor,anchor+'\n UPROPERTY(VisibleAnywhere,Category="Player visuals") TObjectPtr<ULocalKartDriverVisuals> LocalDriverVisuals;',1)
    blob=git('hash-object','-w','--stdin',data=base.encode()).decode().strip()
    git('update-index','--add','--cacheinfo','100644',blob,path)
files=[]
for folder in ['Art/PlayerVisuals/FirstPerson','Content/RoadToF1/PlayerVisuals/FirstPerson']:
    files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix not in ['.blend1','.pyc'] and '__pycache__' not in p.parts]
v5=ROOT/'Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5'
files += [p for p in v5.iterdir() if p.is_file() and p.suffix in ['.blend','.json','.png','.md']]
kart=ROOT/'Art/DesertKarting/Kart'
files += [kart/n for n in ['Kart_Reference.blend','README.md','kart_manifest.json','build_kart.py']]
for folder in ['Textures','Exports','Renders']:
    files += [p for p in (kart/folder).rglob('*') if p.is_file()]
files += [ROOT/p for p in ['Source/Road_To_F1_New/LocalKartDriverVisuals.cpp','Source/Road_To_F1_New/LocalKartDriverVisuals.h','Source/Road_To_F1_New/Tests/LocalKartDriverVisualsTests.cpp','Tools/import_first_person.py','Tools/PreviewFirstPerson.ps1','Evidence/FirstPerson/validation_summary.json','Evidence/FirstPerson/import.json','Evidence/FirstPerson/ue_center.png','Evidence/FirstPerson/ue_left.png','Evidence/FirstPerson/ue_right.png','Evidence/FirstPerson/Automation/index.json']]
assert all(p.exists() for p in files)
assert all(p.stat().st_size<100*1024**2 for p in files), 'File exceeds GitHub size limit'
git('add','--',*[str(p.relative_to(ROOT)).replace('\\','/') for p in files])
print('STAGED_DELIVERY',len(files),'files',round(sum(p.stat().st_size for p in files)/1024**2,1),'MiB')
