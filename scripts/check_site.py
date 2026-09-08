#!/usr/bin/env python3
"""Validate rendered pages and same-site links without any network requests."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.errors: list[str] = []
        self.h1 = 0
        self.feed(text)
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        a = dict(attrs)
        if a.get('id'):
            self.ids.append(a['id'])
        if tag == 'h1':
            self.h1 += 1
        for name in ('href', 'src'):
            if name in a:
                value = a[name] or ''
                if not value.strip() or value == '#':
                    self.errors.append(f'Empty {name} on <{tag}>')
                else:
                    self.links.append((tag, value))
        if tag == 'img' and not a.get('alt'):
            self.errors.append('Image missing alternative text')

def validate(root: Path, base_url: str) -> list[str]:
    root = root.resolve()
    if not (root / 'index.html').is_file():
        return ['Missing index.html; run Hugo first.']
    errors: list[str] = []
    pages: dict[Path, Page] = {}
    for file in root.rglob('*.html'):
        text = file.read_text(encoding='utf-8')
        page = Page(text)
        pages[file] = page
        errors.extend(f'{file.relative_to(root)}: {e}' for e in page.errors)
        if len(page.ids) != len(set(page.ids)):
            errors.append(f'{file.relative_to(root)}: duplicate IDs')
        if '#ZgotmplZ' in text:
            errors.append(f'{file.relative_to(root)}: unsafe/unrenderable template URL')
        for sample in ('Alex Johnson', '10,000 citations', 'Your Name'):
            if sample in text:
                errors.append(f'{file.relative_to(root)}: starter identity remains: {sample}')
    for rel in ('index.html', 'zh/index.html'):
        file = root / rel
        if file not in pages:
            errors.append(f'Missing language homepage: {rel}')
            continue
        home = pages[file]
        if home.h1 != 1:
            errors.append(f'{rel}: homepage must have exactly one h1')
        for section in ('main', 'about', 'recruitment', 'publications', 'funding', 'experience'):
            if section not in home.ids:
                errors.append(f'{rel}: missing homepage landmark: {section}')
    base = urlsplit(base_url)
    prefix = base.path.rstrip('/')
    for file, page in pages.items():
        for tag, value in page.links:
            u = urlsplit(value)
            if u.scheme in ('javascript', 'file'):
                errors.append(f'{file.name}: forbidden URL scheme: {u.scheme}')
                continue
            if u.scheme in ('mailto', 'tel', 'data'):
                continue
            if u.netloc and u.netloc.lower() != base.netloc.lower():
                continue
            path = unquote(u.path)
            if prefix and (path == prefix or path.startswith(prefix + '/')):
                path = path[len(prefix):] or '/'
            target = file if not path else ((root / path.lstrip('/')) if path.startswith('/') else (file.parent / path))
            target = target.resolve()
            if not target.is_relative_to(root):
                errors.append(f'{file.name}: path escapes output directory: {value}')
                continue
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                errors.append(f'{file.name}: missing local target: {value}')
            elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
                errors.append(f'{file.name}: missing anchor: {value}')
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--base-url', default='https://ewardnewget.github.io/')
    args = parser.parse_args()
    errors = validate(args.directory, args.base_url)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print('Generated HTML, local assets and anchors: PASS (no external network checks).')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
