"""One-time audit of unchanged original CV facts; not run by maintenance CI.
Run explicitly: python -m unittest discover -s tests -p audit_initial_content.py -v
Only use this snapshot audit for the original supplied CV, not subsequent updates.
"""
import unittest
from test_content import load

class InitialSourceAudit(unittest.TestCase):
    def test_seed_author_order(self):
        papers = {p["id"]: p for p in load("data/publications.yaml")["papers"]}
        self.assertEqual(papers["icse-2024-pointer-flow"]["authors"],
                         ["Yuqi Guo", "Shihao Zhu", "Yan Cai", "Liang He", "Jian Zhang"])
        self.assertEqual(papers["icse-2025-dependence"]["authors"][0], "Shihao Zhu")

    def test_seed_funding_does_not_invent_dates(self):
        grants = {g["id"]: g for g in load("data/funding.yaml")["principal"]}
        self.assertEqual(grants["postdoc-c"]["amount_wan"], 24)
        self.assertEqual(grants["nsfc-c"]["amount_wan"], 30)
        self.assertEqual(grants["ccf-huyanglin"]["amount_wan"], 50)
        self.assertNotIn("period", grants["nsfc-c"])
        self.assertNotIn("year", grants["nsfc-c"])
        self.assertEqual(grants["ccf-huyanglin"]["period"], "2026.01–2026.12")

    def test_only_source_month_precision_is_used(self):
        p = load("data/authors/me.yaml")
        self.assertEqual(p["experience"][0]["period"], "2025.07–present")
        self.assertEqual(p["education"][0]["period"], "2019.09–2025.07")
        self.assertEqual(p["education"][1]["period"], "2015.09–2019.06")


if __name__ == "__main__":
    unittest.main()
