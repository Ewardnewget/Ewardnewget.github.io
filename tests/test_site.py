"""Validate either real Hugo output or the explicitly labelled offline preview."""
import importlib.util
import os
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = Path(os.environ.get('SITE_DIR', str(ROOT / 'public'))).resolve()

class SiteTests(unittest.TestCase):
    def setUp(self):
        self.docs = {}
        for lang, rel in [('en', 'index.html'), ('zh', 'zh/index.html')]:
            path = SITE / rel
            self.assertTrue(path.is_file(), f'Render both languages first: {path}')
            self.docs[lang] = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        self.papers = yaml.safe_load((ROOT / 'data/publications.yaml').read_text())['papers']
        self.settings = yaml.safe_load((ROOT / 'data/settings.yaml').read_text())

    def test_identity_and_semantic_landmarks(self):
        for lang, d in self.docs.items():
            self.assertEqual(len(d.select('h1')), 1)
            self.assertEqual(d.h1.get_text(), '祝世豪' if lang == 'zh' else 'Shihao Zhu')
            self.assertTrue(d.html['lang'].startswith(lang))
            for selector in ('main#main', '#about', '#recruitment', '#publications', '#funding', '#experience'):
                self.assertIsNotNone(d.select_one(selector))

    def test_native_language_links_and_seo(self):
        for lang, d in self.docs.items():
            self.assertEqual({a['hreflang'] for a in d.select('.language-switch a')}, {'en', 'zh'})
            self.assertEqual(d.select_one('.language-switch a[aria-current="page"]')['hreflang'], lang)
            self.assertEqual({a['hreflang'] for a in d.select('link[rel="alternate"]')}, {'en', 'zh', 'x-default'})
            self.assertIsNotNone(d.select_one('link[rel="canonical"]'))

    def test_navigation_and_ids(self):
        for d in self.docs.values():
            ids = [x['id'] for x in d.select('[id]')]
            self.assertEqual(len(ids), len(set(ids)))
            for a in d.select('a[href^="#"]'):
                self.assertIn(a['href'][1:], ids)

    def test_unified_publications_preserve_authors_and_order(self):
        for d in self.docs.values():
            rows = d.select('#paper-list > li')
            self.assertEqual(len(rows), len(self.papers))
            years = [int(p['data-year']) for p in rows if p['data-year'] != 'undated']
            self.assertEqual(years, sorted(years, reverse=True))
            for paper in self.papers:
                row = d.find(id=paper['id'])
                self.assertEqual(row.select_one('.paper-authors').get_text(), ', '.join(paper['authors']) + '.')
                self.assertEqual(len(row.select('.author-self')), 1)
                self.assertEqual(row['data-year'], str(paper.get('year', 'undated')))
            self.assertFalse(d.select('[data-scope], [data-lead], .cofirst, .paper-authors sup'))

    def test_accepted_status_is_localized(self):
        for lang, d in self.docs.items():
            for p in self.papers:
                if p.get('status') == 'accepted':
                    self.assertEqual(d.find(id=p['id']).select_one('.accepted').get_text(), '已录用' if lang == 'zh' else 'Accepted')

    def test_honors_switch_controls_navigation_and_html(self):
        for d in self.docs.values():
            expected = self.settings['show_honors']
            self.assertEqual(bool(d.select('#honors')), expected)
            self.assertEqual(bool(d.select('a[href="#honors"]')), expected)
            self.assertFalse(d.select('.ip-records'))

    def test_about_research_merged_and_recruitment_follows(self):
        for d in self.docs.values():
            self.assertFalse(d.select('#research, a[href="#research"]'))
            self.assertEqual(d.select_one('#about').find_next_sibling().get('id'), 'recruitment')
            self.assertIsNotNone(d.select_one('#recruitment a[href^="mailto:"]'))

    def test_english_has_no_chinese_prose_except_language_label(self):
        # Paper titles and author names remain in their original publication language.
        english = BeautifulSoup(str(self.docs['en']), 'html.parser')
        english.select_one('.language-switch').decompose()
        self.assertNotRegex(english.body.get_text(), r'[\u4e00-\u9fff]')
        zh = self.docs['zh'].get_text()
        for untranslated in ('Last updated', 'As principal investigator', 'Contact by email', 'Search title'):
            self.assertNotIn(untranslated, zh)

    def test_logos_and_contacts(self):
        profile = yaml.safe_load((ROOT / 'data/authors/me.yaml').read_text())
        expected = len(profile['experience']) + len(profile['education'])
        for d in self.docs.values():
            self.assertEqual(len(d.select('#experience img.institution-logo')), expected)
            for img in d.select('img'):
                self.assertTrue(img.get('alt'))
            self.assertIn(profile['email_display'], d.select_one('#about').get_text())
            self.assertIsNotNone(d.select_one(f'a[href="mailto:{profile["email"]}"]'))

    def test_core_content_does_not_require_javascript(self):
        for d in self.docs.values():
            self.assertIsNotNone(d.select_one('#publication-controls[hidden]'))
            self.assertFalse(d.select('#paper-list li[hidden]'))
            self.assertTrue(d.select('details summary'))
            self.assertGreater(len(d.select('#funding .grant')), 0)
            self.assertFalse(d.select('script[src^="http"]'))
            self.assertFalse(d.select('link[rel="stylesheet"][href^="http"]'))

    def test_no_built_with_private_cv_or_demo(self):
        for d in self.docs.values():
            visible = d.get_text(' ')
            for word in ('Built with', 'Alex Johnson', 'Your Name', '政治面貌', '软件著作权', '专利'):
                self.assertNotIn(word, visible)
            self.assertNotRegex(visible, r'(?<!\d)1[3-9]\d{9}(?!\d)')
        self.assertFalse(list(SITE.rglob('简历_中文_有作者信息.pdf')))

    def test_all_local_resources_and_links_resolve(self):
        spec = importlib.util.spec_from_file_location('check_site', ROOT / 'scripts/check_site.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        base = os.environ.get('SITE_BASE_URL', 'https://ewardnewget.github.io/')
        self.assertEqual(module.validate(SITE, base), [])

if __name__ == '__main__':
    unittest.main()
