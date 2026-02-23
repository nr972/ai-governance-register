"""LLM-assisted risk classification using the Anthropic API."""

import json
import os
from typing import Optional

from anthropic import Anthropic

CLASSIFICATION_SYSTEM_PROMPT = """You are an EU AI Act compliance expert. Given a description \
of an AI system, classify it according to the EU AI Act risk tiers.

Risk tiers:
- UNACCEPTABLE: Prohibited practices (Article 5) — social scoring by governments, \
real-time remote biometric identification in public spaces for law enforcement \
(with narrow exceptions), exploitation of vulnerable groups, subliminal manipulation \
causing harm.
- HIGH: Systems listed in Annex III — biometric identification, critical infrastructure, \
education, employment, essential services, law enforcement, migration/border, \
justice/democracy. Also: safety components of regulated products.
- LIMITED: Systems with transparency obligations (Article 52) — chatbots, emotion \
recognition, deepfake generation.
- MINIMAL: All other AI systems — no specific obligations, voluntary codes of conduct.

Respond with ONLY a JSON object (no markdown, no code fences):
{
    "risk_tier": "unacceptable|high|limited|minimal",
    "confidence": 0.0-1.0,
    "reasoning": "2-3 sentence explanation citing specific EU AI Act articles/annexes",
    "relevant_annex_categories": ["list of relevant Annex III category names if any"]
}"""


async def classify_with_llm(
    system_description: str,
    purpose: Optional[str] = None,
    data_inputs: Optional[str] = None,
) -> dict:
    """Send system description to Claude for risk classification suggestion.

    Returns a dict with keys: suggested_risk_tier, confidence, reasoning,
    relevant_annex_categories, method.

    Raises ``ValueError`` if ``ANTHROPIC_API_KEY`` is not configured.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "LLM-assisted classification requires an Anthropic API key."
        )

    client = Anthropic(api_key=api_key)

    user_message = f"AI System Description: {system_description}"
    if purpose:
        user_message += f"\nPurpose/Use Case: {purpose}"
    if data_inputs:
        user_message += f"\nData Inputs: {data_inputs}"

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=CLASSIFICATION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    response_text = message.content[0].text
    result = json.loads(response_text)

    return {
        "suggested_risk_tier": result["risk_tier"],
        "confidence": result["confidence"],
        "reasoning": result["reasoning"],
        "relevant_annex_categories": result.get("relevant_annex_categories", []),
        "method": "llm_assisted",
    }
