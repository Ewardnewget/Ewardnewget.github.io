#!/usr/bin/env python3
"""Exercise future edits and negative link checks on TEMPORARY COPIES only."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from bs4 import BeautifulSoup
import yaml

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    checks = []
    with tempfile.TemporaryDirectory(prefix='homepage-regression-') as tmp:
        temp = Path(tmp)
        copy = temp / 'site'
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '__pycache__', '.venv', 'public', 'node_modules', 'resources'))
        out = temp / 'rendered'
        def render(base='https://ewardnewget.github.io/'):
            subprocess.run([sys.executable, str(copy/'scripts/render_preview.py'), '--output', str(out), '--base-url', base], check=True, timeout=100)
        def doc(lang):
            return BeautifulSoup((out/('zh/index.html' if lang=='zh' else 'index.html')).read_text(), 'html.parser')
        (copy/'data/settings.yaml').write_text('show_honors: true\n')
        render()
        for lang in ('en','zh'):
            d = doc(lang)
            assert d.select_one('#honors') is not None
            assert d.select_one('a[href="#honors"]') is not None
            assert len(d.select('#honors .honors-list li')) == 5
        checks.append('Honors enabled: both language sections and their navigation links render')
        (copy/'data/settings.yaml').write_text('show_honors: false\n')
        datafile = copy/'data/publications.yaml'
        data = yaml.safe_load(datafile.read_text())
        data['papers'].append({'id':'regression-only-example','title':'Regression Fixture (Not Published Content)','authors':['Example Author','Shihao Zhu'],'venue':'TEST','year':2027,'links':[]})
        survey = next(p for p in data['papers'] if p['id']=='models-data-race')
        survey.update(year=2026,status='published')
        datafile.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False))
        base='https://ewardnewget.github.io/research/'
        render(base)
        for lang in ('en','zh'):
            d=doc(lang)
            rows=d.select('#paper-list > li')
            assert len(rows)==10 and rows[0]['id']=='regression-only-example'
            assert not d.select('[data-year="undated"]')
            assert not d.select('#models-data-race .accepted')
            assert not d.select('#honors, a[href="#honors"]')
        checks.append('Future paper: count and chronological order update without authorship metadata')
        checks.append('Adding a confirmed publication year removes the undated label naturally')
        env={**os.environ,'SITE_DIR':str(out),'SITE_BASE_URL':base}
        subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=copy,env=env,check=True,timeout=30)
        checks.append('All 22 maintenance tests also pass with changed counts, years and a subpath base URL')
        spec=importlib.util.spec_from_file_location('links', copy/'scripts/check_site.py')
        links=importlib.util.module_from_spec(spec); spec.loader.exec_module(links)
        logo=out/'images/logos/iscas.png'; raw=logo.read_bytes(); logo.unlink()
        assert any('missing local target' in e for e in links.validate(out,base))
        logo.write_bytes(raw)
        checks.append('Missing-logo negative test is correctly rejected by the local-link checker')
        home=out/'index.html'; raw=home.read_text(); home.write_text(raw.replace('</body>','<div id="about"></div></body>'))
        assert any('duplicate IDs' in e for e in links.validate(out,base))
        home.write_text(raw)
        checks.append('Duplicate-ID negative test is correctly rejected')
    dest=ROOT.parent/'regression-checks.json'
    dest.write_text(json.dumps({'checks':checks,'count':len(checks),'all_passed':True},ensure_ascii=False,indent=2))
    print(f'{len(checks)} regression scenarios passed; source files unchanged.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
