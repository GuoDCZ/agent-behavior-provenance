"""Reproduce local validation, preserving real checks and labeling synthetic demos.

No LLM/API calls. Fresh destination directories are mandatory.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from provenance.report import analyze,compare
from tests.fixtures_generator import make_run


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--results',type=Path,required=True)
    a=p.parse_args(); runs=a.runs.resolve(); out=a.results.resolve()
    if runs.exists() or out.exists(): p.error('Choose fresh --runs and --results directories; existing evidence is not overwritten')
    runs.mkdir(parents=True); out.mkdir(parents=True)
    def cmd(args,cwd,log,expected=0):
        result=subprocess.run([sys.executable,*args],cwd=cwd,capture_output=True,text=True)
        (out/log).write_text('$ python '+ ' '.join(args)+'\n'+result.stdout+result.stderr+f'\nEXIT_CODE={result.returncode}; EXPECTED={expected}\n')
        if result.returncode!=expected: raise RuntimeError(f'Unexpected exit: see {out/log}')
    def originals():
        return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for directory in ('workload','skills','scripts','scenarios','tests') for p in (ROOT/'artifact'/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    before=originals()
    cmd(['-m','unittest','discover','-s','tests','-v'],ROOT/'artifact','professor-helper-tests.txt')
    cmd(['tools/run_tests.py'],ROOT/'artifact/workload','original-workload-tests.txt',1)
    cmd(['-m','unittest','discover','-s','tests','-v'],ROOT,'analyzer-tests.txt')
    statuses={name:shutil.which(name) for name in ('opencode','pi')}
    (out/'environment.json').write_text(json.dumps({'python':sys.version,'agents':statuses,'live_collection':'not_attempted_by_local_validation','blocker':'No OpenCode or Pi binary; no managed credentials configured' if not any(statuses.values()) else 'See live collection protocol; this command is offline only','references_missing':[n for n in ('Project.pdf','project-guide.pdf','project_a.md') if not (ROOT/n).exists()]},indent=2)+'\n')
    for scenario,name in [('normal','normal-001'),('tool-output-injection','tool-output-001')]:
        run=runs/name
        cmd(['artifact/scripts/prepare.py',scenario,'--output',str(run)],ROOT,f'{name}-prepare.txt')
        cmd(['artifact/scripts/check.py',str(run)],ROOT,f'{name}-check.txt',1)
        analyze(run,out/name,snapshot_only=True)
    compare(out/'normal-001/analysis.json',out/'tool-output-001/analysis.json',out/'comparison.md')
    demo=out/'synthetic-unit-test-demonstrations'; demo.mkdir()
    (demo/'README.md').write_text('SYNTHETIC UNIT-TEST OUTPUTS ONLY. Not real agent experiments. Inputs retained under the --runs directory, synthetic-fixtures/.\n')
    for case in ('normal','injection','unknown','attempt','malformed'):
        run=make_run(runs/'synthetic-fixtures'/case,case)
        analyze(run,demo/case)
    unchanged=before==originals()
    (out/'source_integrity.json').write_text(json.dumps({'unchanged':unchanged,'sha256':before},indent=2)+'\n')
    if not unchanged: raise RuntimeError('Professor originals changed')
    print(f'Local checks and outputs saved to {out}. No real agent trajectories were collected.')

if __name__=='__main__': main()
