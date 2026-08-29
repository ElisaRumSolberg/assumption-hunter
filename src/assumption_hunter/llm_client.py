import json
import os
import re

from dotenv import load_dotenv
from google import genai

load_dotenv()

_client: genai.Client | None = None

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")


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
    response = gemini_client().models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return (response.text or "").strip()


def extract_json(text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else text
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output: {text[:200]}")
    return json.loads(candidate[start : end + 1])
