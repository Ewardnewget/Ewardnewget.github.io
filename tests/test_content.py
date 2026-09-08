"""Maintenance checks: validate editable data without pinning publication counts or years."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    p = ROOT / path
    if not p.is_file():
        raise AssertionError(f'Required content file is missing: {path}')
    return yaml.safe_load(p.read_text(encoding='utf-8'))

class ContentTests(unittest.TestCase):
    def test_profile_identity_and_contacts(self):
        p = load('data/authors/me.yaml')
        self.assertEqual(p['name']['display'], 'Shihao Zhu')
        self.assertEqual(p['name']['alternate'], '祝世豪')
        for field in ('email', 'secondary_email'):
            if p.get(field):
                self.assertRegex(p[field], r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        self.assertTrue(p['email_display'])
        self.assertIn('YnaAB10AAAAJ', p['scholar'])

    def test_publications_have_unique_ids_and_ordered_authors(self):
        papers = load('data/publications.yaml')['papers']
        self.assertTrue(papers)
        self.assertEqual(len({p['id'] for p in papers}), len(papers))
        for p in papers:
            self.assertRegex(p['id'], r'^[a-z0-9-]+$')
            self.assertTrue(p['title'].strip())
            self.assertIn('Shihao Zhu', p['authors'])
            self.assertEqual(len(p['authors']), len(set(p['authors'])))
            self.assertNotIn('lead', p)
            self.assertNotIn('cofirst', p)
            for link in p.get('links', []):
                self.assertRegex(link['url'], r'^(https://|/)')
                self.assertTrue(link['label'].strip())

    def test_accepted_papers_can_omit_unconfirmed_year(self):
        for p in load('data/publications.yaml')['papers']:
            self.assertTrue(p['venue'])
            if 'year' in p:
                self.assertIsInstance(p['year'], int)
                self.assertGreater(p['year'], 1900)
            else:
                self.assertEqual(p.get('status'), 'accepted')
            if 'status' in p:
                self.assertIn(p['status'], ['accepted', 'published'])

    def test_funding_is_positive_and_bilingual(self):
        for g in load('data/funding.yaml')['principal']:
            self.assertGreater(g['amount_wan'], 0)
            self.assertEqual(g['role'], 'Principal investigator')
            self.assertTrue(g['name'])
            self.assertTrue(g['name_zh'])
            if g.get('project_title'):
                self.assertTrue(g['project_title_zh'])
        for g in load('data/funding.yaml')['participating']:
            for key in ('title', 'programme', 'role'):
                self.assertTrue(g[key])
                self.assertTrue(g[key + '_zh'])

    def test_separate_source_roots_keep_demo_content_out(self):
        config = load('config/_default/hugo.yaml')
        mounts = load('config/_default/module.yaml')['mounts']
        self.assertIn({'source': 'site-content', 'target': 'content'}, mounts)
        self.assertIn({'source': 'site-static', 'target': 'static'}, mounts)
        self.assertTrue((ROOT / 'layouts/_partials/researcher/paper.html').is_file())
        self.assertEqual(config['baseURL'], 'https://ewardnewget.github.io/')

    def test_languages_default_to_english_and_have_content(self):
        config = load('config/_default/hugo.yaml')
        self.assertEqual(config['defaultContentLanguage'], 'en')
        self.assertFalse(config['defaultContentLanguageInSubdir'])
        self.assertEqual(set(load('config/_default/languages.yaml')), {'en', 'zh'})
        for name in ('_index.md', '_index.zh.md'):
            text = (ROOT / 'site-content' / name).read_text(encoding='utf-8')
            meta = yaml.safe_load(text.split('---', 2)[1])
            self.assertTrue(meta['summary'])
            self.assertTrue(meta['recruitment'])

    def test_ui_translation_keys_match(self):
        en, zh = load('data/ui/en.yaml'), load('data/ui/zh.yaml')
        self.assertEqual(set(en), set(zh))
        for lang in (en, zh):
            self.assertIn('{visible}', lang['count_pattern'])
            self.assertIn('{total}', lang['count_pattern'])
            self.assertTrue(all(isinstance(v, str) for v in lang.values()))

    def test_experience_month_precision_and_original_local_logos(self):
        p = load('data/authors/me.yaml')
        for r in p['experience'] + p['education']:
            self.assertRegex(r['period'], r'^\d{4}\.\d{2}–(present|\d{4}\.\d{2})$')
            logo = (ROOT / 'site-static' / r['logo']).resolve()
            self.assertTrue(logo.is_relative_to(ROOT / 'site-static'))
            self.assertTrue(logo.is_file())
            self.assertGreater(logo.stat().st_size, 100)

    def test_honors_configuration_keeps_data_but_no_ip_data(self):
        self.assertIsInstance(load('data/settings.yaml')['show_honors'], bool)
        data = load('data/records.yaml')
        self.assertEqual(set(data), {'honors'})
        self.assertTrue(data['honors'])
        for row in data['honors']:
            self.assertTrue(row['title'])
            self.assertTrue(row['title_zh'])
        self.assertTrue((ROOT / 'layouts/_partials/researcher/records.html').is_file())

    def test_no_private_cv_fields_or_demo_identity(self):
        files = list((ROOT / 'data').rglob('*.yaml')) + list((ROOT / 'site-content').rglob('*.md'))
        for p in files:
            text = p.read_text(encoding='utf-8')
            self.assertNotRegex(text, r'(?m)^\s*(phone|age|political_affiliation):')
            self.assertNotRegex(text, r'(?<!\d)1[3-9]\d{9}(?!\d)')
            self.assertNotIn('Alex Johnson', text)
        self.assertFalse(list((ROOT / 'site-static').rglob('简历_中文_有作者信息.pdf')))

if __name__ == '__main__':
    unittest.main()
