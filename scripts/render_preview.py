#!/usr/bin/env python3
"""Reproducible OFFLINE Go-template preview; not a complete Hugo build.
Requires Python 3.10+, Go, PyYAML, markdown-it-py, and BeautifulSoup4.
"""
from __future__ import annotations
import argparse
import base64
import copy
import json
import mimetypes
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load_data() -> dict:
    result = {}
    for file in sorted((ROOT / 'data').rglob('*.yaml')):
        keys = file.relative_to(ROOT / 'data').with_suffix('').parts
        target = result
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        target[keys[-1]] = yaml.safe_load(file.read_text(encoding='utf-8'))
    return result

def front_matter(file: Path) -> tuple[dict, str]:
    text = file.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError(f'Missing YAML front matter: {file}')
    _, header, body = text.split('---', 2)
    return yaml.safe_load(header), body.strip()

def self_contained(html: str, output: Path, base_url: str) -> str:
    """Embed local assets and connect the two local HTML documents."""
    doc = BeautifulSoup(html, 'html.parser')
    prefix = urlsplit(base_url).path.rstrip('/')
    def asset(url: str) -> Path:
        path = urlsplit(url).path
        if prefix and path.startswith(prefix + '/'):
            path = path[len(prefix):]
        resolved = (output / path.lstrip('/')).resolve()
        if not resolved.is_relative_to(output.resolve()):
            raise ValueError('Asset path escapes preview directory')
        return resolved
    for node in doc.select('link[rel="stylesheet"]'):
        style = doc.new_tag('style')
        style.string = asset(node['href']).read_text(encoding='utf-8')
        node.replace_with(style)
    for node in doc.select('script[src]'):
        script = doc.new_tag('script')
        script.string = "document.addEventListener('DOMContentLoaded', () => {\n" + asset(node['src']).read_text(encoding='utf-8') + '\n});'
        node.replace_with(script)
    for node in doc.select('img[src], link[rel="icon"]'):
        attr = 'src' if node.name == 'img' else 'href'
        path = asset(node[attr])
        mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        node[attr] = f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')
    for link in doc.select('.language-switch a'):
        link['href'] = f'shihao-zhu-{link["hreflang"]}.html'
    return str(doc)

def bilingual_viewer(pages: dict[str, str]) -> str:
    """Convenience viewer only; the production site still uses separate URLs."""
    doc = BeautifulSoup('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Shihao Zhu</title><style>html,body{margin:0;width:100%;height:100%;overflow:hidden}iframe{border:0;width:100%;height:100%;display:block}</style></head><body><iframe title="Academic homepage preview"></iframe></body></html>', 'html.parser')
    doc.iframe['srcdoc'] = pages['en']
    payload = doc.new_tag('script', type='application/json', id='translated-pages')
    payload.string = json.dumps(pages, ensure_ascii=False).replace('<', '\\u003c')
    doc.body.append(payload)
    script = doc.new_tag('script')
    script.string = """
const pages = JSON.parse(document.getElementById('translated-pages').textContent);
const frame = document.querySelector('iframe');
let pendingHash = '';
frame.addEventListener('load', () => {
  if (pendingHash) {
    const id = decodeURIComponent(pendingHash.slice(1));
    const target = frame.contentDocument.getElementById(id);
    if (target) target.scrollIntoView({behavior: 'instant'});
    pendingHash = '';
  }
  frame.contentDocument.querySelectorAll('.language-switch a').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      const lang = link.getAttribute('hreflang');
      pendingHash = frame.contentWindow.location.hash;
      document.documentElement.lang = lang;
      document.title = lang === 'zh' ? '祝世豪' : 'Shihao Zhu';
      frame.srcdoc = pages[lang];
    });
  });
});
"""
    doc.body.append(script)
    return str(doc)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT.parent / 'preview')
    parser.add_argument('--standalone', type=Path, help='Also write embedded-assets HTML previews here')
    parser.add_argument('--base-url', default='https://ewardnewget.github.io/')
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT.is_relative_to(output):
        raise ValueError('Choose a separate output directory, not the source root or its parent')
    go = shutil.which('go')
    if not go:
        raise RuntimeError('Go is required for this template preview')
    markdown = MarkdownIt('commonmark', {'html': False})
    data = load_data()
    base = args.base_url.rstrip('/') + '/'
    prefix = urlsplit(base).path
    translations = [dict(Language={'Lang': lang}, RelPermalink=prefix + ('zh/' if lang == 'zh' else ''), Permalink=base + ('zh/' if lang == 'zh' else '')) for lang in ('en', 'zh')]
    pages = []
    rendered_markdown = {}
    for lang in ('en', 'zh'):
        meta, body = front_matter(ROOT / 'site-content' / ('_index.zh.md' if lang == 'zh' else '_index.md'))
        translated = next(p for p in translations if p['Language']['Lang'] == lang)
        site = {'Data': data, 'Language': {'Lang': lang}, 'Home': translated, 'BaseURL': base}
        page = {**translated, 'Site': site, 'Params': meta, 'Content': markdown.render(body), 'AllTranslations': translations, 'output': 'zh/index.html' if lang == 'zh' else 'index.html', 'template': 'home.html'}
        pages.append(page)
        rendered_markdown[meta['recruitment']] = markdown.render(meta['recruitment'])
        error_page = copy.copy(page)
        error_page.update(output='zh/404.html' if lang == 'zh' else '404.html', template='404.html')
        pages.append(error_page)
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'site-static', output, dirs_exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='homepage-render-') as temp:
        payload = Path(temp) / 'render.json'
        payload.write_text(json.dumps({'root': str(ROOT), 'output': str(output), 'base_url': base, 'pages': pages, 'markdown': rendered_markdown}, ensure_ascii=False), encoding='utf-8')
        env = {**os.environ, 'GO111MODULE': 'off', 'GOTOOLCHAIN': 'local'}
        subprocess.run([go, 'run', str(ROOT / 'scripts/preview_renderer.go'), str(payload)], env=env, check=True, timeout=90)
    if args.standalone:
        dest = args.standalone.resolve()
        dest.mkdir(parents=True, exist_ok=True)
        single = {}
        for lang in ('en', 'zh'):
            html = (output / ('zh/index.html' if lang == 'zh' else 'index.html')).read_text(encoding='utf-8')
            single[lang] = self_contained(html, output, base)
            (dest / f'shihao-zhu-{lang}.html').write_text(single[lang], encoding='utf-8')
        (dest / 'shihao-zhu-preview.html').write_text(bilingual_viewer(single), encoding='utf-8')
    print('Offline template preview created. Complete Hugo/HugoBlox integration remains a separate check.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
