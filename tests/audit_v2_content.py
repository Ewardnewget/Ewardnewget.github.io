"""Acceptance tests for the user's second-round edits (source and rendered output)."""
import os
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = Path(os.environ.get('SITE_DIR', str(ROOT / 'public'))).resolve()

def load(name):
    path = ROOT / name
    if not path.is_file():
        raise AssertionError(f'Missing required data: {name}')
    return yaml.safe_load(path.read_text(encoding='utf-8'))

class RevisionContentTests(unittest.TestCase):
    def test_survey_is_accepted_and_has_no_invented_date(self):
        p = next((p for p in load('data/publications.yaml')['papers'] if p['id'] == 'models-data-race'), None)
        self.assertIsNotNone(p, 'The accepted survey must be in the unified papers list')
        self.assertEqual(p['status'], 'accepted')
        self.assertNotIn('year', p)
        self.assertNotIn('doi', p)
        self.assertEqual(p['authors'], ['Shihao Zhu', 'Yan Cai', 'Jian Zhang'])

    def test_no_authorship_categories_in_data(self):
        for p in load('data/publications.yaml')['papers']:
            self.assertNotIn('lead', p)
            self.assertNotIn('cofirst', p)

    def test_only_honors_data_is_retained_and_disabled(self):
        records = load('data/records.yaml')
        self.assertTrue(records['honors'])
        self.assertNotIn('patents', records)
        self.assertNotIn('software', records)
        self.assertIs(load('data/settings.yaml')['show_honors'], False)
        self.assertTrue((ROOT / 'layouts/_partials/researcher/records.html').is_file())

    def test_experience_education_have_real_local_logos(self):
        p = load('data/authors/me.yaml')
        for row in p['experience'] + p['education']:
            self.assertIn('logo', row)
            self.assertTrue((ROOT / 'site-static' / row['logo']).is_file())
        self.assertEqual(p['experience'][0]['logo'], p['education'][0]['logo'])
        self.assertNotEqual(p['education'][0]['logo'], p['education'][1]['logo'])

    def test_languages_and_default(self):
        config = load('config/_default/hugo.yaml')
        self.assertEqual(config['defaultContentLanguage'], 'en')
        self.assertFalse(config['defaultContentLanguageInSubdir'])
        self.assertEqual(set(load('config/_default/languages.yaml')), {'en', 'zh'})
        self.assertTrue((ROOT / 'site-content/_index.zh.md').is_file())

    def test_new_email_keeps_existing_contact(self):
        p = load('data/authors/me.yaml')
        self.assertEqual(p['email'], 'zhush@ios.ac.cn')
        self.assertEqual(p['email_display'], 'zhush_aT_ios.ac.cn')
        self.assertEqual(p['secondary_email'], 'zshpeking@gmail.com')

class RevisionRenderedTests(unittest.TestCase):
    def document(self, language):
        path = SITE / ('zh/index.html' if language == 'zh' else 'index.html')
        self.assertTrue(path.is_file(), f'Missing separate {language} page')
        return BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')

    def test_bilingual_documents_and_switches(self):
        for lang in ('en', 'zh'):
            with self.subTest(lang=lang):
                d = self.document(lang)
                self.assertTrue(d.html['lang'].startswith(lang))
                links = d.select('.language-switch a')
                self.assertEqual({a['hreflang'] for a in links}, {'en', 'zh'})
                self.assertEqual(len(d.select('.language-switch a[aria-current="page"]')), 1)
                self.assertEqual(d.select_one('.language-switch a[aria-current="page"]')['hreflang'], lang)
                self.assertEqual(len(d.select('link[rel="alternate"][hreflang]')), 3)

    def test_survey_is_in_same_list_without_authorship_filters(self):
        for lang in ('en', 'zh'):
            with self.subTest(lang=lang):
                d = self.document(lang)
                p = d.select_one('#paper-list > #models-data-race')
                self.assertIsNotNone(p)
                self.assertIn('已录用' if lang == 'zh' else 'Accepted', p.get_text())
                self.assertFalse(d.select('[data-scope], [data-lead], .cofirst, #manuscripts'))
                self.assertFalse(d.select('.paper-authors sup'))

    def test_removed_sections_absent_and_about_merged(self):
        for lang in ('en', 'zh'):
            with self.subTest(lang=lang):
                d = self.document(lang)
                self.assertFalse(d.select('#research, #honors, .ip-records, a[href="#honors"], a[href="#research"]'))
                self.assertNotIn('Built with', d.get_text())
                for removed in ('专利', '软件著作权', 'Patents', 'software copyrights'):
                    self.assertNotIn(removed, d.get_text())
                about = d.select_one('#about .biography').get_text(' ')
                self.assertIn('并发软件安全' if lang == 'zh' else 'concurrent software security', about)

    def test_recruitment_immediately_after_about_and_exact_chinese_copy(self):
        for lang in ('en', 'zh'):
            with self.subTest(lang=lang):
                d = self.document(lang)
                self.assertEqual(d.select_one('#about').find_next_sibling().get('id'), 'recruitment')
                r = d.select_one('#recruitment')
                self.assertIsNotNone(r)
                self.assertIsNotNone(r.select_one('a[href="mailto:zhush@ios.ac.cn"]'))
        r = self.document('zh').select_one('#recruitment').get_text(' ', strip=True)
        for expected in ('计算机专业', '基础知识扎实', '动手能力强', '每周工作4天以上', '最少实习3个月', '软件所保研或推免名额'):
            self.assertIn(expected, r.replace(' ', ''))

    def test_logos_and_both_email_links_in_both_languages(self):
        for lang in ('en', 'zh'):
            with self.subTest(lang=lang):
                d = self.document(lang)
                self.assertEqual(len(d.select('#experience img.institution-logo')), 3)
                for image in d.select('#experience img.institution-logo'):
                    self.assertTrue(image.get('alt'))
                self.assertIn('zhush_aT_ios.ac.cn', d.select_one('#about').get_text())
                self.assertIsNotNone(d.select_one('#about a[href="mailto:zhush@ios.ac.cn"]'))
                self.assertIsNotNone(d.select_one('#about a[href="mailto:zshpeking@gmail.com"]'))

if __name__ == '__main__':
    unittest.main()
