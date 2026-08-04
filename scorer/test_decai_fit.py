#!/usr/bin/env python3
"""Tests for the DecAI Fit reference scorer. Run: python test_decai_fit.py"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from decai_fit import FLAG_NAMES, score  # noqa: E402

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def make_card(days: int = 100, **overrides) -> dict:
    flags = {name: 0 for name in FLAG_NAMES}
    flags.update(overrides)
    return {"project_id": "test-project", "flags": flags, "last_verified_days": days}


class TestBlockScores(unittest.TestCase):
    def test_ai_score_is_capped_at_3(self):
        result = score(make_card(AI_0=1, AI_1=1, AI_2=1, AI_3=1, AI_4=1))
        self.assertEqual(result.ai_score, 3)

    def test_tokenless_project_gets_fixed_2(self):
        result = score(make_card(AI_1=1, TK_0=1))
        self.assertEqual(result.token_score, 2)

    def test_replaceable_token_subtracts(self):
        result = score(make_card(AI_1=1, TK_1=1, TK_2=1, TK_4=1))
        self.assertEqual(result.token_score, 1)

    def test_token_score_clamped_at_zero(self):
        result = score(make_card(AI_1=1, TK_4=1))
        self.assertEqual(result.token_score, 0)


class TestBaseMapping(unittest.TestCase):
    EXPECTED = {0: 1, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5, 11: 6, 12: 6}

    def test_all_sums(self):
        for total, expected_base in self.EXPECTED.items():
            base = max(1, (total + 1) // 2)
            self.assertEqual(base, expected_base, f"S={total}")


class TestCaps(unittest.TestCase):
    def test_r0_zero_ai_forces_zero(self):
        result = score(make_card(OC_1=1, OC_2=1, TK_1=1, E_OC_T1=1))
        self.assertEqual(result.ai_score, 0)
        self.assertEqual(result.final, 0)

    def test_r1_tier3_only_caps_at_2(self):
        # Strong flags but Tier-3-only sourcing must not exceed 2.
        result = score(
            make_card(AI_1=1, AI_2=1, AI_3=1, OC_1=1, OC_2=1, OC_3=1, TK_0=1, E_only_T3=1)
        )
        self.assertLessEqual(result.final, 2)
        self.assertTrue(any("R1" in cap for cap in result.caps_applied))

    def test_r2_missing_core_evidence_caps_at_3(self):
        result = score(
            make_card(AI_1=1, AI_2=1, AI_3=1, OC_1=1, OC_2=1, OC_3=1, TK_0=1,
                      E_OC_T1=1, E_TK_T1=1)  # E_AI_T1 = 0
        )
        self.assertLessEqual(result.final, 3)
        self.assertTrue(any("R2" in cap for cap in result.caps_applied))

    def test_r3_unverified_token_caps_at_4(self):
        result = score(
            make_card(AI_1=1, AI_2=1, AI_3=1, OC_1=1, OC_2=1, OC_3=1,
                      TK_1=1, TK_2=1, E_AI_T1=1, E_OC_T1=1)  # token, E_TK_T1 = 0
        )
        self.assertLessEqual(result.final, 4)
        self.assertTrue(any("R3" in cap for cap in result.caps_applied))

    def test_r4_shallow_ai_caps_total(self):
        # ai_score = 1 caps at 3 even with everything else maximal.
        result = score(
            make_card(AI_1=1, OC_1=1, OC_2=1, OC_3=1, TK_1=1, TK_2=1, TK_3=1,
                      E_AI_T1=1, E_OC_T1=1, E_TK_T1=1)
        )
        self.assertEqual(result.ai_score, 1)
        self.assertLessEqual(result.final, 3)

    def test_perfect_project_scores_6(self):
        result = score(
            make_card(AI_1=1, AI_2=1, AI_3=1, AI_4=1, OC_1=1, OC_2=1, OC_3=1,
                      TK_1=1, TK_2=1, E_AI_T1=1, E_OC_T1=1, E_TK_T1=1)
        )
        self.assertEqual(result.final, 6)
        self.assertEqual(result.caps_applied, [])


class TestStaleness(unittest.TestCase):
    def test_stale_card_loses_one_point(self):
        fresh = make_card(days=550, AI_1=1, AI_2=1, AI_3=1, AI_4=1, OC_1=1, OC_2=1, OC_3=1,
                          TK_1=1, TK_2=1, E_AI_T1=1, E_OC_T1=1, E_TK_T1=1)
        stale = dict(fresh, last_verified_days=551)
        self.assertEqual(score(fresh).final, 6)
        self.assertEqual(score(stale).final, 5)

    def test_stale_penalty_never_goes_below_1_when_ai_present(self):
        result = score(make_card(days=600, AI_0=1, E_only_T3=1))
        self.assertEqual(result.final, 1)

    def test_stale_zero_ai_stays_zero(self):
        result = score(make_card(days=600, OC_1=1))
        self.assertEqual(result.final, 0)


class TestValidation(unittest.TestCase):
    def test_missing_flag_raises(self):
        card = make_card()
        del card["flags"]["AI_0"]
        with self.assertRaises(ValueError):
            score(card)

    def test_non_binary_flag_raises(self):
        card = make_card()
        card["flags"]["AI_1"] = 2
        with self.assertRaises(ValueError):
            score(card)

    def test_intent_flag_with_working_ai_warns(self):
        result = score(make_card(AI_0=1, AI_1=1))
        self.assertTrue(any("AI_0" in w for w in result.warnings))


class TestPublishedExamples(unittest.TestCase):
    """The examples/ directory must always match the documented outputs."""

    EXPECTED = {
        "strong_project.json": 6,
        "mid_project.json": 4,
        "weak_project.json": 1,
        "zero_project.json": 0,
    }

    def test_examples(self):
        for filename, expected in self.EXPECTED.items():
            card = json.loads((EXAMPLES_DIR / filename).read_text(encoding="utf-8"))
            self.assertEqual(score(card).final, expected, filename)


if __name__ == "__main__":
    unittest.main(verbosity=2)
