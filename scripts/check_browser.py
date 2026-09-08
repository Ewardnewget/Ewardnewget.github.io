#!/usr/bin/env python3
"""Offline in-memory browser checks; no network or file-URL navigation.
Requires Playwright and Chromium. Real site routing is checked separately.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--standalone', type=Path, required=True)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--browser', default='/usr/bin/chromium')
    parser.add_argument('--viewer', type=Path)
    args = parser.parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    documents = {lang: (args.standalone / f'shihao-zhu-{lang}.html').read_text(encoding='utf-8') for lang in ('en', 'zh')}
    results, errors = [], []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        results.append({'check': name, 'result': 'PASS'})
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.browser, headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
        page.on('pageerror', lambda e: errors.append(str(e)))
        for lang in ('en', 'zh'):
            page.set_content(documents[lang], wait_until='load')
            rows = page.locator('#paper-list > li')
            total = rows.count()
            check(f'{lang}: nine unified papers', total == 9)
            check(f'{lang}: accepted survey is included', page.locator('#models-data-race .accepted').count() == 1)
            check(f'{lang}: no authorship filters', page.locator('[data-scope], [data-lead], .cofirst').count() == 0)
            page.locator('#paper-year').select_option('2024')
            check(f'{lang}: year filter', page.locator('#paper-list > li:visible').count() == 1)
            page.locator('#paper-year').select_option('undated')
            check(f'{lang}: undated accepted work filter', page.locator('#paper-list > li:visible').count() == 1 and page.locator('#models-data-race').is_visible())
            page.locator('#paper-year').select_option('all')
            page.locator('#paper-search').fill('SOUND prediction')
            check(f'{lang}: case-insensitive AND search', page.locator('#paper-list > li:visible').count() == 3)
            page.locator('#paper-search').fill('no-match-xyz')
            check(f'{lang}: empty-state message', page.locator('#no-papers').is_visible() and page.locator('#paper-list > li:visible').count() == 0)
            page.locator('#clear-filters').click()
            check(f'{lang}: clear filters', page.locator('#paper-list > li:visible').count() == total)
            count = page.locator('#paper-count').inner_text()
            check(f'{lang}: localized counter', ('显示' in count) if lang=='zh' else ('papers' in count))
            page.locator('details summary').click()
            check(f'{lang}: project disclosure', page.locator('details[open] .project-history article').count() == 4)
            page.locator('details summary').click()
            check(f'{lang}: honors omitted', page.locator('#honors, a[href="#honors"]').count() == 0)
            check(f'{lang}: new mailto', page.locator('#about a[href="mailto:zhush@ios.ac.cn"]').count() == 1)
            page.locator('#experience').scroll_into_view_if_needed()
            page.wait_for_timeout(250)
            loaded = page.locator('img.institution-logo').evaluate_all('(images) => images.every(i => i.complete && i.naturalWidth > 0)')
            check(f'{lang}: institution logos loaded', loaded)
            page.locator('#experience').screenshot(path=str(args.artifacts / f'experience-{lang}.png'))
            for width in (320, 360, 390, 540, 768, 850, 1024, 1440):
                page.set_viewport_size({'width': width, 'height': 1000})
                page.wait_for_timeout(60)
                check(f'{lang}: no horizontal overflow at {width}px', page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'))
            page.set_viewport_size({'width':1440,'height':1000})
            page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
            page.wait_for_timeout(100)
            page.screenshot(path=str(args.artifacts / f'desktop-{lang}.png'), full_page=True)
            page.screenshot(path=str(args.artifacts / f'desktop-{lang}-first-screen.png'))
            page.set_viewport_size({'width':390,'height':844})
            page.screenshot(path=str(args.artifacts / f'mobile-{lang}.png'), full_page=True)
            page.screenshot(path=str(args.artifacts / f'mobile-{lang}-first-screen.png'))
        for locale in ('en-US','zh-CN'):
            context = browser.new_context(java_script_enabled=False, locale=locale)
            nojs = context.new_page()
            nojs.set_content(documents['en'], wait_until='load')
            check(f'{locale}: English entry remains English without JS', nojs.locator('h1').inner_text() == 'Shihao Zhu')
            check(f'{locale}: all papers readable without JS', nojs.locator('#paper-list > li:visible').count() == 9 and not nojs.locator('#publication-controls').is_visible())
            check(f'{locale}: native Chinese destination remains in HTML', nojs.locator('.language-switch a[hreflang="zh"]').get_attribute('href') == 'shihao-zhu-zh.html')
            nojs.set_content(documents['zh'], wait_until='load')
            check(f'{locale}: separate Chinese page works without JS', nojs.locator('h1').inner_text() == '祝世豪')
            nojs.locator('details summary').click()
            check(f'{locale}: native disclosure works without JS', nojs.locator('details[open]').count() == 1)
            context.close()
        if args.viewer:
            page.set_content(args.viewer.read_text(encoding='utf-8'), wait_until='load')
            frame = page.frame_locator('iframe')
            check('single-file viewer defaults to English', frame.locator('h1').inner_text() == 'Shihao Zhu')
            frame.locator('.language-switch a[hreflang="zh"]').click()
            frame.locator('h1').filter(has_text='祝世豪').wait_for()
            check('single-file viewer switches to Chinese', frame.locator('h1').inner_text() == '祝世豪')
            frame.locator('.language-switch a[hreflang="en"]').click()
            frame.locator('h1').filter(has_text='Shihao Zhu').wait_for()
            check('single-file viewer switches back to English', frame.locator('h1').inner_text() == 'Shihao Zhu')
        check('no uncaught browser script errors', not errors)
        browser.close()
    (args.artifacts / 'browser-checks.json').write_text(json.dumps({'checks': results, 'count': len(results), 'page_errors': errors}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(results)} browser checks passed; screenshots saved to {args.artifacts}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
