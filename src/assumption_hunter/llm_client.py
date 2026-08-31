import json
import logging
import os
import re
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

# Silences google-genai's "Direct use of AFC in generate_content is not
# recommended" notice: harmless here since we never pass tools, but it's
# noisy in a terminal recording.
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

_client: genai.Client | None = None

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")

# The Vertex AI connection in this environment occasionally drops mid-request
# (RemoteProtocolError / DNS resolution failures) with no relation to prompt
# content. A short retry with backoff turns those into non-events instead of
# pipeline failures.
MAX_RETRIES = 5
RETRY_BACKOFF_SECONDS = 2


def gemini_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
        )
    return _client


def generate_text(prompt: str) -> str:
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = gemini_client().models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            return (response.text or "").strip()
        except Exception as exc:  # noqa: BLE001 - transient network/API errors
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    raise last_error


def extract_json(text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else text
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output: {text[:200]}")
    return json.loads(candidate[start : end + 1])
