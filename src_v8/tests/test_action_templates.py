"""
Tests for F-3 — Action Templates YAML
========================================
Tests the ActionTemplateEngine (core/action_templates.py) and the
YAML templates (config/action_templates.yaml).

Covers:
  - YAML loading and parsing
  - Trigger evaluation logic
  - Template matching against signal contexts
  - Plan filtering
  - Priority ordering
  - Convenience functions
  - Edge cases
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Test YAML loading
# ─────────────────────────────────────────────────────────────────────────────

class TestTemplateLoading:
    """Test loading templates from YAML files."""

    def test_import(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        assert engine is not None

    def test_default_yaml_loads(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        assert engine.template_count > 0

    def test_default_has_expected_templates(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        ids = engine.template_ids
        assert "high_momentum_positive" in ids
        assert "high_momentum_negative" in ids
        assert "emerging_signal" in ids
        assert "appropriation_risk" in ids
        assert "unknown_circle" in ids

    def test_template_count_matches_yaml(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        # Our YAML has 9 templates
        assert engine.template_count == 9

    def test_load_custom_yaml(self):
        from core.action_templates import ActionTemplateEngine
        # Create temp YAML
        yaml_content = """
test_template:
  name: "Test Template"
  description: "For testing"
  triggers:
    momentum: ">= 50"
  actions:
    - priority: 1
      action: "Test action"
      detail: "Test detail"
      type: "test"
  metadata:
    urgency: "low"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            tmp_path = f.name

        try:
            engine = ActionTemplateEngine(yaml_path=tmp_path)
            assert engine.template_count >= 1
            assert "test_template" in engine.template_ids
        finally:
            os.unlink(tmp_path)

    def test_load_nonexistent_file(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine(yaml_path="/nonexistent/file.yaml")
        assert engine.template_count == 0

    def test_get_template_by_id(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        t = engine.get_template("high_momentum_positive")
        assert t is not None
        assert "Alta Ressonância" in t["name"]

    def test_get_nonexistent_template(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        assert engine.get_template("nonexistent") is None


# ─────────────────────────────────────────────────────────────────────────────
# Test trigger parsing and evaluation
# ─────────────────────────────────────────────────────────────────────────────

class TestTriggerEvaluation:
    """Test the trigger parsing and evaluation logic."""

    def test_parse_gte(self):
        from core.action_templates import _parse_trigger
        op, val = _parse_trigger(">= 70")
        assert op == ">="
        assert val == 70

    def test_parse_lt(self):
        from core.action_templates import _parse_trigger
        op, val = _parse_trigger("< 0.4")
        assert op == "<"
        assert val == 0.4

    def test_parse_eq_string(self):
        from core.action_templates import _parse_trigger
        op, val = _parse_trigger("== youtube")
        assert op == "=="
        assert val == "youtube"

    def test_parse_eq_special(self):
        from core.action_templates import _parse_trigger
        op, val = _parse_trigger("== emergente_desconhecido")
        assert op == "=="
        assert val == "emergente_desconhecido"

    def test_evaluate_gte_true(self):
        from core.action_templates import _evaluate_trigger
        assert _evaluate_trigger(75, ">=", 70) is True

    def test_evaluate_gte_false(self):
        from core.action_templates import _evaluate_trigger
        assert _evaluate_trigger(65, ">=", 70) is False

    def test_evaluate_lt_true(self):
        from core.action_templates import _evaluate_trigger
        assert _evaluate_trigger(0.3, "<", 0.4) is True

    def test_evaluate_eq_string(self):
        from core.action_templates import _evaluate_trigger
        assert _evaluate_trigger("youtube", "==", "youtube") is True

    def test_evaluate_eq_case_insensitive(self):
        from core.action_templates import _evaluate_trigger
        assert _evaluate_trigger("YouTube", "==", "youtube") is True

    def test_evaluate_none_value(self):
        from core.action_templates import _evaluate_trigger
        assert _evaluate_trigger(None, ">=", 70) is False

    def test_evaluate_contains(self):
        from core.action_templates import _evaluate_trigger
        assert _evaluate_trigger("musica_brasileira", "contains", "musica") is True

    def test_evaluate_ne(self):
        from core.action_templates import _evaluate_trigger
        assert _evaluate_trigger("reddit", "!=", "youtube") is True


# ─────────────────────────────────────────────────────────────────────────────
# Test recommendation matching
# ─────────────────────────────────────────────────────────────────────────────

class TestRecommendationMatching:
    """Test that templates match correctly against signal contexts."""

    def test_high_momentum_positive_matches(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 80, "sentiment": 0.8}
        recs = engine.get_recommendations(context)
        template_ids = [r.template_id for r in recs]
        assert "high_momentum_positive" in template_ids

    def test_high_momentum_negative_matches(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 75, "sentiment": 0.2}
        recs = engine.get_recommendations(context, plan="pro")
        template_ids = [r.template_id for r in recs]
        assert "high_momentum_negative" in template_ids

    def test_emerging_signal_matches(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 30, "velocity": 3.0}
        recs = engine.get_recommendations(context)
        template_ids = [r.template_id for r in recs]
        assert "emerging_signal" in template_ids

    def test_appropriation_risk_matches(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"appropriation_risk": 0.8}
        recs = engine.get_recommendations(context, plan="pro")
        template_ids = [r.template_id for r in recs]
        assert "appropriation_risk" in template_ids

    def test_unknown_circle_matches(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"circle": "emergente_desconhecido"}
        recs = engine.get_recommendations(context, plan="pro")
        template_ids = [r.template_id for r in recs]
        assert "unknown_circle" in template_ids

    def test_youtube_high_engagement_matches(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"platform": "youtube", "momentum": 65}
        recs = engine.get_recommendations(context)
        template_ids = [r.template_id for r in recs]
        assert "youtube_high_engagement" in template_ids

    def test_no_match_when_triggers_not_met(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 10, "sentiment": 0.5}
        recs = engine.get_recommendations(context)
        # low momentum, neutral sentiment — shouldn't match high_momentum templates
        template_ids = [r.template_id for r in recs]
        assert "high_momentum_positive" not in template_ids
        assert "high_momentum_negative" not in template_ids

    def test_empty_context_returns_empty(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        recs = engine.get_recommendations({})
        assert recs == []


# ─────────────────────────────────────────────────────────────────────────────
# Test plan filtering
# ─────────────────────────────────────────────────────────────────────────────

class TestPlanFiltering:
    """Test that plan-gated templates are filtered correctly."""

    def test_free_plan_sees_free_templates(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 80, "sentiment": 0.8}
        recs = engine.get_recommendations(context, plan="free")
        # high_momentum_positive has plan_minimum: free
        assert any(r.template_id == "high_momentum_positive" for r in recs)

    def test_free_plan_cannot_see_pro_templates(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 80, "sentiment": 0.2}
        recs = engine.get_recommendations(context, plan="free")
        # high_momentum_negative has plan_minimum: pro
        assert not any(r.template_id == "high_momentum_negative" for r in recs)

    def test_pro_plan_sees_pro_templates(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 80, "sentiment": 0.2}
        recs = engine.get_recommendations(context, plan="pro")
        assert any(r.template_id == "high_momentum_negative" for r in recs)

    def test_enterprise_sees_all(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"appropriation_risk": 0.9}
        recs = engine.get_recommendations(context, plan="enterprise")
        assert any(r.template_id == "appropriation_risk" for r in recs)


# ─────────────────────────────────────────────────────────────────────────────
# Test urgency ordering
# ─────────────────────────────────────────────────────────────────────────────

class TestUrgencyOrdering:
    """Test that recommendations are ordered by urgency."""

    def test_critical_before_high(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        # Context that matches both critical and high urgency
        context = {
            "momentum": 80,
            "sentiment": 0.2,
            "appropriation_risk": 0.8,
        }
        recs = engine.get_recommendations(context, plan="pro")
        if len(recs) >= 2:
            urgencies = [r.urgency for r in recs]
            if "critical" in urgencies and "high" in urgencies:
                crit_idx = urgencies.index("critical")
                high_idx = urgencies.index("high")
                assert crit_idx < high_idx


# ─────────────────────────────────────────────────────────────────────────────
# Test ActionRecommendation structure
# ─────────────────────────────────────────────────────────────────────────────

class TestActionRecommendationStructure:
    """Test the structure of returned recommendations."""

    def test_recommendation_has_actions(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 80, "sentiment": 0.8}
        recs = engine.get_recommendations(context)
        assert len(recs) > 0
        rec = recs[0]
        assert len(rec.actions) > 0

    def test_actions_have_priority(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 80, "sentiment": 0.8}
        recs = engine.get_recommendations(context)
        for rec in recs:
            for action in rec.actions:
                assert action.priority > 0
                assert action.action  # non-empty
                assert action.type  # non-empty

    def test_actions_sorted_by_priority(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 80, "sentiment": 0.8}
        recs = engine.get_recommendations(context)
        for rec in recs:
            priorities = [a.priority for a in rec.actions]
            assert priorities == sorted(priorities)

    def test_metadata_fields_present(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 80, "sentiment": 0.8}
        recs = engine.get_recommendations(context)
        for rec in recs:
            assert rec.urgency in ("critical", "high", "medium", "low")
            assert rec.time_horizon  # non-empty
            assert rec.plan_minimum in ("free", "pro", "executive", "enterprise")


# ─────────────────────────────────────────────────────────────────────────────
# Test convenience functions
# ─────────────────────────────────────────────────────────────────────────────

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_get_action_engine_singleton(self):
        from core.action_templates import get_action_engine
        e1 = get_action_engine()
        e2 = get_action_engine()
        assert e1 is e2

    def test_get_recommendations_function(self):
        from core.action_templates import get_recommendations
        recs = get_recommendations({"momentum": 80, "sentiment": 0.8})
        assert len(recs) > 0

    def test_get_actions_flat(self):
        from core.action_templates import get_actions_flat
        actions = get_actions_flat({"momentum": 80, "sentiment": 0.8})
        assert len(actions) > 0
        assert all(isinstance(a, str) for a in actions)

    def test_flat_respects_max(self):
        from core.action_templates import get_actions_flat
        actions = get_actions_flat(
            {"momentum": 80, "sentiment": 0.8, "volume": 15},
            plan="enterprise",
        )
        assert len(actions) <= 10  # default max_actions

    def test_max_results_limit(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 80, "sentiment": 0.8, "volume": 15}
        recs = engine.get_recommendations(context, plan="enterprise", max_results=2)
        assert len(recs) <= 2


# ─────────────────────────────────────────────────────────────────────────────
# Test declining signal template
# ─────────────────────────────────────────────────────────────────────────────

class TestDecliningSignal:
    """Test the declining_signal template specifically."""

    def test_declining_matches(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 60, "velocity": -3.0}
        recs = engine.get_recommendations(context)
        template_ids = [r.template_id for r in recs]
        assert "declining_signal" in template_ids

    def test_not_declining_when_velocity_positive(self):
        from core.action_templates import ActionTemplateEngine
        engine = ActionTemplateEngine()
        context = {"momentum": 60, "velocity": 5.0}
        recs = engine.get_recommendations(context)
        template_ids = [r.template_id for r in recs]
        assert "declining_signal" not in template_ids


# ─────────────────────────────────────────────────────────────────────────────
# Count
# ─────────────────────────────────────────────────────────────────────────────
# TestTemplateLoading:               8
# TestTriggerEvaluation:            12
# TestRecommendationMatching:        8
# TestPlanFiltering:                 4
# TestUrgencyOrdering:               1
# TestActionRecommendationStructure: 4
# TestConvenienceFunctions:          5
# TestDecliningSignal:               2
# ─────────────────────────────────────────────────────────────────
# TOTAL:                            44
