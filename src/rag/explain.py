import json
import os
from typing import Dict, List, Optional

from src.rag.prompts import (
    PERSONALITY_EXPLANATION_PROMPT,
    SIMILAR_USERS_SECTION,
    NO_LLM_TEMPLATE,
)
from src.config import TRAIT_NAMES


class PersonalityExplainer:
    def __init__(self, use_openai: bool = None):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        if use_openai is None:
            self.use_openai = bool(self.openai_key)
        else:
            self.use_openai = use_openai and bool(self.openai_key)

        if self.use_openai:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_key)

    def explain(
        self,
        predicted_traits: Dict[str, float],
        evidence: Dict[str, List[Dict]],
        similar_users: Optional[List[Dict]] = None,
        user_text: Optional[str] = None,
    ) -> Dict:
        if self.use_openai:
            return self._explain_with_llm(predicted_traits, evidence, similar_users)
        else:
            return self._explain_rule_based(predicted_traits, evidence, similar_users)

    def _explain_with_llm(
        self,
        predicted_traits: Dict[str, float],
        evidence: Dict[str, List[Dict]],
        similar_users: Optional[List[Dict]] = None,
    ) -> Dict:
        traits_json = json.dumps(predicted_traits, indent=2)

        evidence_formatted = {}
        for trait, tweets in evidence.items():
            evidence_formatted[trait] = [
                {"text": t["tweet"][:200], "relevance_score": round(t["score"], 4)}
                for t in tweets[:3]
            ]
        evidence_json = json.dumps(evidence_formatted, indent=2)

        similar_users_section = ""
        if similar_users:
            similar_json = json.dumps(
                [
                    {
                        "traits": u["traits"],
                        "sample_text": u["document"][:200] + "...",
                    }
                    for u in similar_users[:2]
                ],
                indent=2,
            )
            similar_users_section = SIMILAR_USERS_SECTION.format(
                similar_users_json=similar_json
            )

        prompt = PERSONALITY_EXPLANATION_PROMPT.format(
            traits_json=traits_json,
            evidence_json=evidence_json,
            similar_users_section=similar_users_section,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a personality psychology expert. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1500,
            )

            content = response.choices[0].message.content
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            result = json.loads(content)

            if "predicted_traits" not in result:
                result["predicted_traits"] = predicted_traits
            if "evidence" not in result:
                result["evidence"] = evidence

            return result

        except Exception as e:
            result = self._explain_rule_based(predicted_traits, evidence, similar_users)
            result["llm_error"] = str(e)
            return result

    def _explain_rule_based(
        self,
        predicted_traits: Dict[str, float],
        evidence: Dict[str, List[Dict]],
        similar_users: Optional[List[Dict]] = None,
    ) -> Dict:
        trait_explanations = {}
        for trait in TRAIT_NAMES:
            score = predicted_traits.get(trait, 0.5)
            level = "high" if score > 0.6 else "moderate" if score > 0.4 else "low"

            base_explanation = NO_LLM_TEMPLATE["trait_explanations"].get(
                trait, f"Analysis for {trait}."
            )
            trait_explanations[trait] = f"Score: {score:.2f} ({level}). {base_explanation}"

            if trait in evidence and evidence[trait]:
                sample_tweet = evidence[trait][0]["tweet"][:100]
                trait_explanations[trait] += f" Example: '{sample_tweet}...'"

        result = {
            "predicted_traits": predicted_traits,
            "evidence": evidence,
            "trait_explanations": trait_explanations,
            "overall_summary": NO_LLM_TEMPLATE["overall_summary"],
            "caveats": NO_LLM_TEMPLATE["caveats"],
        }

        if similar_users:
            result["similar_users"] = [
                {"traits": u["traits"], "similarity": 1 - u.get("distance", 0)}
                for u in similar_users[:3]
            ]

        return result


def get_explainer(use_openai: bool = None) -> PersonalityExplainer:
    return PersonalityExplainer(use_openai=use_openai)

