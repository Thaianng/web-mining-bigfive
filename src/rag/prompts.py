PERSONALITY_EXPLANATION_PROMPT = """You are a personality analysis expert. Based on the predicted Big Five personality traits and evidence from the user's posts, provide a detailed explanation.

## Predicted Personality Traits (scale 0-1):
{traits_json}

## Evidence Posts (grouped by trait):
{evidence_json}

{similar_users_section}

## Task:
Analyze the predicted personality traits and explain why each trait received its score based on the evidence. Be specific and reference actual content from the posts.

Provide your response in the following JSON format:
{{
    "predicted_traits": {{
        "open": <float>,
        "conscientious": <float>,
        "extroverted": <float>,
        "agreeable": <float>,
        "stable": <float>
    }},
    "trait_explanations": {{
        "open": "<explanation for openness score>",
        "conscientious": "<explanation for conscientiousness score>",
        "extroverted": "<explanation for extraversion score>",
        "agreeable": "<explanation for agreeableness score>",
        "stable": "<explanation for emotional stability score>"
    }},
    "overall_summary": "<2-3 sentence summary of the personality profile>",
    "caveats": [
        "This analysis is based on limited social media posts",
        "Personality is complex and may not be fully captured by text analysis",
        "Results should be interpreted as tendencies, not absolute traits"
    ]
}}

Important notes:
- "stable" refers to Emotional Stability (low neuroticism)
- Scores closer to 1 indicate higher levels of that trait
- Base explanations on actual evidence, not assumptions
- Be balanced and avoid overly positive or negative characterizations"""

SIMILAR_USERS_SECTION = """
## Similar Users (for reference):
These users have similar writing patterns. Their actual trait scores are shown for context:
{similar_users_json}
"""

NO_LLM_TEMPLATE = {
    "trait_explanations": {
        "open": "Based on text analysis, this score reflects the user's interest in new ideas and experiences as evidenced by their vocabulary and topics.",
        "conscientious": "This score is derived from language patterns indicating organization, responsibility, and goal-oriented behavior.",
        "extroverted": "The extraversion score reflects social language, mentions of activities, and overall communication style.",
        "agreeable": "This score is based on cooperative language, empathy expressions, and interpersonal warmth in the posts.",
        "stable": "Emotional stability is assessed through calm language patterns and absence of anxiety/stress indicators.",
    },
    "overall_summary": "This personality profile is generated using machine learning analysis of the provided posts. The scores represent tendencies on a 0-1 scale.",
    "caveats": [
        "This analysis is based on limited social media posts and should not be considered a clinical assessment.",
        "Personality is complex and cannot be fully captured through text analysis alone.",
        "Results should be interpreted as behavioral tendencies, not fixed personality traits.",
        "The 'stable' trait refers to emotional stability (inverse of neuroticism).",
    ],
}

