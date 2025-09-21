"""
prompt-util.py

Provides getPromptFromTemplate(...) which accepts a BasePromptTemplate (or a dict with the same shape)
and returns a filled prompt along with which parameter values were chosen.

This version imports the Pydantic models directly from models/db_models.py:
    - ParameterValueDistribution
    - PromptParameterDetails
    - BasePromptTemplate
"""

from __future__ import annotations
import re
import random
from typing import Any, Dict, List, Optional, Union

# Import the models directly as requested
from models.db_models import (
    ParameterValueDistribution,
    PromptParameterDetails,
    BasePromptTemplate,
)


_PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")


def _normalize_probabilities(distributions: List[Dict[str, Any]]) -> List[float]:
    """Take a sequence of {'value': ..., 'probability': ...} and return normalized probs.
       If all probabilities are zero or missing, return uniform distribution.
    """
    probs: List[float] = []
    for d in distributions:
        try:
            p = float(d.get("probability", 0.0))
        except Exception:
            p = 0.0
        if p < 0:
            p = 0.0
        probs.append(p)
    total = sum(probs)
    if total <= 0:
        n = len(probs) if len(probs) > 0 else 1
        return [1.0 / n] * len(probs)
    return [p / total for p in probs]


def _pick_one_value(distributions: List[Dict[str, Any]]) -> str:
    """Normalize probabilities and pick one value using random.choices"""
    if not distributions:
        return ""
    values = [str(d.get("value", "")) for d in distributions]
    probs = _normalize_probabilities(distributions)
    picked = random.choices(values, weights=probs, k=1)[0]
    return picked


def _pick_multiple_values(distributions: List[Dict[str, Any]]) -> List[str]:
    """For chooseMultiple == True: do independent Bernoulli trials for each distribution entry.
       Probability is clamped to [0,1]. If probability > 1 treat as 1.
    """
    results: List[str] = []
    for d in distributions:
        value = str(d.get("value", ""))
        try:
            p = float(d.get("probability", 0.0))
        except Exception:
            p = 0.0
        if p <= 0.0:
            continue
        if p >= 1.0:
            results.append(value)
            continue
        if random.random() < p:
            results.append(value)
    return results


def _normalize_vdist_items(vdist: List[Any]) -> List[Dict[str, Any]]:
    """
    Accept list items which may be:
      - dicts with keys 'value' and 'probability'
      - instances of ParameterValueDistribution (Pydantic model)
    Return a list of plain dicts: {'value': ..., 'probability': ...}
    """
    norm: List[Dict[str, Any]] = []
    for item in vdist:
        if isinstance(item, dict):
            norm.append(item)
        elif isinstance(item, ParameterValueDistribution):
            norm.append({"value": item.value, "probability": item.probability})
        else:
            # Try attribute access for duck-typed objects
            val = getattr(item, "value", None)
            prob = getattr(item, "probability", None)
            norm.append({"value": val, "probability": prob})
    return norm


def _extract_template_and_params(
    template_input: Union[BasePromptTemplate, Dict[str, Any], Any]
) -> tuple[str, List[Any]]:
    """
    Accept:
      - BasePromptTemplate instance
      - dict with keys 'promptTemplate' and 'promptParameterDetailsList'
      - object with attributes of those names
    Return (template_str, promptParameterDetailsList)
    """
    if isinstance(template_input, dict):
        template_str = template_input.get("promptTemplate", "")
        param_list = template_input.get("promptParameterDetailsList", [])
    elif isinstance(template_input, BasePromptTemplate):
        template_str = template_input.promptTemplate
        param_list = template_input.promptParameterDetailsList or []
    else:
        # duck-typed object
        template_str = getattr(template_input, "promptTemplate", "")
        param_list = getattr(template_input, "promptParameterDetailsList", [])
    return template_str, list(param_list or [])


def getPromptFromTemplate(
    template_input: Union[BasePromptTemplate, Dict[str, Any], Any],
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Process a BasePromptTemplate-like object/dict and return chosen parameter values and the prompt.

    Args:
        template_input: BasePromptTemplate instance or dict/object with:
            - promptTemplate: str
            - promptParameterDetailsList: list of PromptParameterDetails-like items
        seed: Optional[int] to seed randomness for reproducibility.

    Returns:
        {
          "prompt": "<filled prompt string>",
          "selections": { "<key>": ["val1", "val2", ...], ... },
          "warnings": [ ... ]
        }
    """
    if seed is not None:
        random.seed(seed)

    template_str, param_details_list = _extract_template_and_params(template_input)
    warnings: List[str] = []
    selections: Dict[str, List[str]] = {}

    # Build a map key -> details
    key_to_details: Dict[str, Any] = {}
    for idx, p in enumerate(param_details_list):
        if isinstance(p, dict):
            key = p.get("key")
            if not key:
                warnings.append(f"Parameter at index {idx} missing 'key'; skipping.")
                continue
            key_to_details[str(key)] = p
        elif isinstance(p, PromptParameterDetails):
            key_to_details[str(p.key)] = p
        else:
            # duck-typed object
            key = getattr(p, "key", None)
            if not key:
                warnings.append(f"Parameter object at index {idx} missing 'key'; skipping.")
                continue
            key_to_details[str(key)] = p

    # For every parameter detail compute selection(s)
    for key, details in key_to_details.items():
        # Extract valueDistribution and chooseMultiple (support dicts, models, or duck-typed)
        if isinstance(details, dict):
            raw_vdist = details.get("valueDistribution", []) or []
            choose_multiple = bool(details.get("chooseMultiple", False))
        elif isinstance(details, PromptParameterDetails):
            raw_vdist = details.valueDistribution or []
            choose_multiple = bool(details.chooseMultiple)
        else:
            raw_vdist = getattr(details, "valueDistribution", []) or []
            choose_multiple = bool(getattr(details, "chooseMultiple", False))

        norm_vdist = _normalize_vdist_items(list(raw_vdist))

        if not norm_vdist:
            warnings.append(f"No valueDistribution provided for parameter '{key}'.")
            selections[key] = []
            continue

        if not choose_multiple:
            chosen = _pick_one_value(norm_vdist)
            selections[key] = [chosen] if chosen != "" else []
        else:
            chosen_list = _pick_multiple_values(norm_vdist)
            selections[key] = chosen_list

    # Replace placeholders in template
    def _replacement(match: re.Match) -> str:
        k = match.group(1)
        if k in selections:
            vals = selections[k]
            if not vals:
                return ""
            return ", ".join(vals)
        else:
            warnings.append(f"Template contains placeholder '{{{{{k}}}}}' but no parameter details were provided.")
            return match.group(0)  # Return the original placeholder unchanged

    filled_prompt = _PLACEHOLDER_PATTERN.sub(_replacement, template_str)

    return {"prompt": filled_prompt, "selections": selections, "warnings": warnings}


# Demo / self-test when run as a script
if __name__ == "__main__":
    demo = {
        "promptTemplate": "You are writing a story about {{theme}}. Use tone: {{tone}}. Add tags: {{tags}}.",
        "promptParameterDetailsList": [
            {
                "key": "theme",
                "valueDistribution": [
                    {"value": "theft", "probability": 0.5},
                    {"value": "domestic_violence", "probability": 0.2},
                    {"value": "jealousy", "probability": 0.3},
                ],
                "chooseMultiple": False,
            },
            {
                "key": "tone",
                "valueDistribution": [
                    {"value": "sombre", "probability": 0.3},
                    {"value": "witty", "probability": 0.7},
                ],
                "chooseMultiple": False,
            },
            {
                "key": "tags",
                "valueDistribution": [
                    {"value": "Victorian", "probability": 0.8},
                    {"value": "mystery", "probability": 0.9},
                    {"value": "courtroom", "probability": 0.1},
                ],
                "chooseMultiple": True,
            },
        ],
    }

    print("Demo run with seed=42")
    out = getPromptFromTemplate(demo, seed=42)
    print("Filled prompt:\n", out["prompt"])
    print("Selections:", out["selections"])
    print("Warnings:", out["warnings"])
