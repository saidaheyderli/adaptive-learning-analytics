"""
Thin wrapper around the Gemini API for generating weakness-targeted
recommendations. Kept isolated in its own module so the rest of the
codebase never talks to the AI SDK directly — only this module knows
about prompt format, model name, and response parsing.
"""

import json
import logging

from django.conf import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

MODEL_NAME = 'gemini-2.5-flash'

RECOMMENDATION_SCHEMA = {
    'type': 'object',
    'properties': {
        'explanation': {
            'type': 'string',
            'description': 'A short, encouraging explanation (2-4 sentences) targeting the specific concept the student is struggling with.',
        },
        'practice_prompt': {
            'type': 'string',
            'description': 'A new multiple-choice practice question on the same topic, at an appropriate difficulty.',
        },
        'practice_choices': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'text': {'type': 'string'},
                    'is_correct': {'type': 'boolean'},
                },
                'required': ['text', 'is_correct'],
            },
            'minItems': 3,
            'maxItems': 5,
        },
    },
    'required': ['explanation', 'practice_prompt', 'practice_choices'],
}


class GeminiRecommendationError(Exception):
    """Raised when the Gemini API call fails or returns an unusable response."""


def _client():
    if not settings.GEMINI_API_KEY:
        raise GeminiRecommendationError('GEMINI_API_KEY is not configured.')
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_recommendation(topic_name: str, accuracy_percent: float, recent_prompts: list[str]) -> dict:
    """
    Ask Gemini for a targeted explanation + a new practice question for a
    student who is weak on `topic_name`.

    `recent_prompts` is a short list of question prompts the student has
    already seen on this topic, so Gemini can avoid generating a duplicate.

    Returns a dict matching RECOMMENDATION_SCHEMA. Raises
    GeminiRecommendationError on any failure — callers should catch this
    and degrade gracefully rather than letting it bubble up as a 500.
    """
    seen = '\n'.join(f'- {p}' for p in recent_prompts) or '(none recorded)'
    prompt = (
        f'A student is practicing the topic "{topic_name}" and is currently '
        f'answering correctly only {accuracy_percent:.0f}% of the time, which is '
        f'below the mastery threshold.\n\n'
        f'Questions they have already seen on this topic:\n{seen}\n\n'
        f'Generate:\n'
        f'1. A short, encouraging explanation (2-4 sentences) that targets the '
        f'likely misconception, without being condescending.\n'
        f'2. One new multiple-choice practice question on the same topic '
        f'(different from the ones already seen), with 3-5 answer choices where '
        f'exactly one is correct.'
    )

    try:
        client = _client()  # keep a reference alive for the duration of the call —
        # calling _client().models.generate_content(...) inline lets Python garbage
        # collect the temporary Client before the request completes, which raises
        # "Cannot send a request, as the client has been closed." (a known issue
        # in google-genai >=1.39.0, see googleapis/python-genai#1763).
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=RECOMMENDATION_SCHEMA,
            ),
        )
        data = json.loads(response.text)
    except Exception as exc:  # noqa: BLE001 - any SDK/parsing failure should degrade gracefully
        logger.exception('Gemini recommendation generation failed for topic=%s', topic_name)
        raise GeminiRecommendationError(str(exc)) from exc

    choices = data.get('practice_choices', [])
    if sum(1 for c in choices if c.get('is_correct')) != 1:
        raise GeminiRecommendationError('Generated choices must have exactly one correct answer.')

    return data
