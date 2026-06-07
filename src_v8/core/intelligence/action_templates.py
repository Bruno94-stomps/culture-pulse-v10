"""
Action Template Engine — F-3 (FASE 1: Fundação)
=================================================
Loads YAML-based action templates and matches them against signal
analysis data to generate recommended actions.

Replaces hardcoded recommendation strings scattered across multiple
engines (authenticity_analyzer, scenario_planning_engine, etc.) with
a single, maintainable YAML file (config/action_templates.yaml).

Usage::

    from core.action_templates import ActionTemplateEngine, get_action_engine

    engine = get_action_engine()

    # Given signal data
    context = {
        "momentum": 75,
        "sentiment": 0.8,
        "authenticity": 0.6,
        "circle": "musica_brasileira",
        "platform": "youtube",
        "velocity": 5.0,
        "volume": 12,
    }

    recommendations = engine.get_recommendations(context)
    # Returns: List[ActionRecommendation] with matched templates + actions

Custom templates:
    engine.load_templates("/path/to/custom_templates.yaml")
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Lazy YAML import ─────────────────────────────────────────────────────────
try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False
    logger.warning("⚠️ PyYAML not installed — action templates unavailable. pip install pyyaml")


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class Action:
    """A single recommended action."""
    priority: int
    action: str
    detail: str
    type: str


@dataclass
class ActionRecommendation:
    """A matched template with its actions."""
    template_id: str
    name: str
    description: str
    actions: List[Action]
    urgency: str = "medium"
    time_horizon: str = ""
    plan_minimum: str = "free"
    match_score: float = 1.0  # how well triggers matched


# ── Trigger evaluation ───────────────────────────────────────────────────────

# Regex to parse trigger expressions like ">= 70", "< 0.4", "== youtube"
_TRIGGER_PATTERN = re.compile(
    r"^\s*(>=|<=|>|<|==|!=|in|contains)\s*(.+)$"
)


def _parse_trigger(expression: str) -> Tuple[str, Any]:
    """Parse a trigger expression into (operator, value)."""
    match = _TRIGGER_PATTERN.match(str(expression).strip())
    if not match:
        # Try as plain value (implicit ==)
        return "==", expression.strip()

    op = match.group(1).strip()
    raw_val = match.group(2).strip()

    # Try numeric
    try:
        val = float(raw_val)
        if val == int(val):
            val = int(val)
        return op, val
    except ValueError:
        pass

    # String value (remove quotes if present)
    if (raw_val.startswith('"') and raw_val.endswith('"')) or \
       (raw_val.startswith("'") and raw_val.endswith("'")):
        raw_val = raw_val[1:-1]

    return op, raw_val


def _evaluate_trigger(actual_value: Any, operator: str, expected_value: Any) -> bool:
    """Evaluate a single trigger condition."""
    if actual_value is None:
        return False

    try:
        if operator == ">=":
            return float(actual_value) >= float(expected_value)
        elif operator == "<=":
            return float(actual_value) <= float(expected_value)
        elif operator == ">":
            return float(actual_value) > float(expected_value)
        elif operator == "<":
            return float(actual_value) < float(expected_value)
        elif operator == "==":
            # String comparison for non-numeric
            if isinstance(expected_value, str):
                return str(actual_value).lower() == expected_value.lower()
            return float(actual_value) == float(expected_value)
        elif operator == "!=":
            if isinstance(expected_value, str):
                return str(actual_value).lower() != expected_value.lower()
            return float(actual_value) != float(expected_value)
        elif operator == "in":
            return str(actual_value).lower() in str(expected_value).lower()
        elif operator == "contains":
            return str(expected_value).lower() in str(actual_value).lower()
    except (ValueError, TypeError):
        return False

    return False


# ── ActionTemplateEngine ─────────────────────────────────────────────────────

class ActionTemplateEngine:
    """
    Loads and evaluates action templates from YAML.

    Supports:
      - Multiple YAML files (merged)
      - Trigger-based matching against signal context
      - Priority ordering of recommendations
      - Plan filtering (free/pro/enterprise)
    """

    DEFAULT_YAML_PATH = Path(__file__).parent.parent / "config" / "action_templates.yaml"

    def __init__(self, yaml_path: Optional[str] = None):
        self._templates: Dict[str, dict] = {}
        self._loaded = False

        if yaml_path:
            self.load_templates(yaml_path)
        else:
            self.load_templates(str(self.DEFAULT_YAML_PATH))

    def load_templates(self, yaml_path: str) -> int:
        """
        Load templates from a YAML file.

        Returns number of templates loaded.
        """
        if not _YAML_AVAILABLE:
            logger.warning("⚠️ PyYAML not available — no templates loaded")
            return 0

        path = Path(yaml_path)
        if not path.exists():
            logger.warning(f"⚠️ Template file not found: {yaml_path}")
            return 0

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                logger.warning(f"⚠️ Invalid template format in {yaml_path}")
                return 0

            self._templates.update(data)
            self._loaded = True
            logger.info(f"✅ Loaded {len(data)} action templates from {path.name}")
            return len(data)

        except Exception as exc:
            logger.error(f"❌ Failed to load templates: {exc}")
            return 0

    @property
    def template_count(self) -> int:
        """Number of loaded templates."""
        return len(self._templates)

    @property
    def template_ids(self) -> List[str]:
        """List of loaded template IDs."""
        return list(self._templates.keys())

    def get_template(self, template_id: str) -> Optional[dict]:
        """Get a specific template by ID."""
        return self._templates.get(template_id)

    def get_recommendations(
        self,
        context: Dict[str, Any],
        plan: str = "free",
        max_results: int = 5,
    ) -> List[ActionRecommendation]:
        """
        Match templates against analysis context and return recommendations.

        Args:
            context: dict with signal data (momentum, sentiment, etc.)
            plan: user plan for filtering (free/pro/enterprise)
            max_results: max number of recommendations to return

        Returns:
            List[ActionRecommendation] sorted by urgency then match_score.
        """
        if not self._templates:
            return []

        plan_rank = {"free": 0, "pro": 1, "executive": 2, "enterprise": 3}
        user_rank = plan_rank.get(plan.lower(), 0)

        matched = []

        for tid, template in self._templates.items():
            triggers = template.get("triggers", {})
            if not triggers:
                continue

            # Check all triggers
            match_count = 0
            total_triggers = len(triggers)

            for var_name, expression in triggers.items():
                actual_value = context.get(var_name)
                op, expected = _parse_trigger(str(expression))
                if _evaluate_trigger(actual_value, op, expected):
                    match_count += 1

            # All triggers must match
            if match_count < total_triggers:
                continue

            # Check plan minimum
            metadata = template.get("metadata", {})
            min_plan = metadata.get("plan_minimum", "free")
            min_rank = plan_rank.get(min_plan, 0)
            if user_rank < min_rank:
                continue

            # Build recommendation
            actions = []
            for a in template.get("actions", []):
                actions.append(Action(
                    priority=a.get("priority", 99),
                    action=a.get("action", ""),
                    detail=a.get("detail", ""),
                    type=a.get("type", ""),
                ))

            match_score = match_count / total_triggers if total_triggers > 0 else 0

            rec = ActionRecommendation(
                template_id=tid,
                name=template.get("name", tid),
                description=template.get("description", ""),
                actions=sorted(actions, key=lambda a: a.priority),
                urgency=metadata.get("urgency", "medium"),
                time_horizon=metadata.get("time_horizon", ""),
                plan_minimum=min_plan,
                match_score=match_score,
            )
            matched.append(rec)

        # Sort: critical > high > medium > low, then by match_score desc
        urgency_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        matched.sort(
            key=lambda r: (urgency_rank.get(r.urgency, 99), -r.match_score)
        )

        return matched[:max_results]

    def get_actions_flat(
        self,
        context: Dict[str, Any],
        plan: str = "free",
        max_actions: int = 10,
    ) -> List[str]:
        """
        Convenience: return flat list of action strings (for backward
        compatibility with engines that use List[str] recommendations).
        """
        recs = self.get_recommendations(context, plan=plan)
        actions = []
        for rec in recs:
            for a in rec.actions:
                actions.append(a.action)
                if len(actions) >= max_actions:
                    return actions
        return actions


# ── Module-level singleton ───────────────────────────────────────────────────

_default_engine: Optional[ActionTemplateEngine] = None


def get_action_engine() -> ActionTemplateEngine:
    """Get or create the module-level ActionTemplateEngine singleton."""
    global _default_engine
    if _default_engine is None:
        _default_engine = ActionTemplateEngine()
    return _default_engine


def get_recommendations(context: Dict[str, Any], plan: str = "free") -> List[ActionRecommendation]:
    """Convenience: get recommendations using the default engine."""
    return get_action_engine().get_recommendations(context, plan=plan)


def get_actions_flat(context: Dict[str, Any], plan: str = "free") -> List[str]:
    """Convenience: get flat action strings using the default engine."""
    return get_action_engine().get_actions_flat(context, plan=plan)
