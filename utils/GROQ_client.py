"""
utils/groq_client.py — Groq AI integration (Free, Cloud-based).

Groq provides a FREE API with generous limits:
    - llama3-70b-8192      : Llama 3 70B  — smartest, recommended
    - llama3-8b-8192       : Llama 3 8B   — fastest
    - mixtral-8x7b-32768   : Mixtral 8x7B — great for long prompts
    - gemma2-9b-it         : Google Gemma 2 — solid alternative

Setup (one-time, 2 minutes):
    1. Go to https://console.groq.com
    2. Sign up (free, no credit card needed)
    3. Click "API Keys" → "Create API Key"
    4. Copy the key (starts with gsk_...)
    5. Paste it in the DataLens app — that's it!

Rate limits (free tier as of 2025):
    - 30 requests/minute
    - 14,400 requests/day
    - 6,000 tokens/minute per model

Uses only Python stdlib — no extra pip packages needed.
"""

import json
import urllib.request
import urllib.error
from typing import Iterator


GROQ_BASE_URL = "https://api.groq.com/openai/v1"
TIMEOUT       = 60   # seconds

# Available free models — (model_id, display_label)
# Updated April 2026 — confirmed active Groq free-tier model IDs.
# Check latest at: console.groq.com/docs/models
GROQ_MODELS = [
    ("llama-3.3-70b-versatile",  "Llama 3.3 70B  (smartest, recommended)"),
    ("llama-3.1-8b-instant",     "Llama 3.1 8B   (fastest)"),
    ("llama3-70b-8192",          "Llama 3 70B    (legacy)"),
    ("llama3-8b-8192",           "Llama 3 8B     (legacy fast)"),
    ("mixtral-8x7b-32768",       "Mixtral 8x7B   (long context)"),
    ("gemma2-9b-it",             "Gemma 2 9B     (Google)"),
]

GROQ_MODEL_IDS = [m[0] for m in GROQ_MODELS]


# ── Exceptions ────────────────────────────────────────────────────────────────

class GroqAPIError(Exception):
    """Raised when Groq returns an error response."""
    pass


class GroqAuthError(Exception):
    """Raised when the API key is invalid or missing."""
    pass


class GroqRateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass


# ── Client ────────────────────────────────────────────────────────────────────

class GroqClient:
    """
    Thin wrapper around the Groq API (OpenAI-compatible).
    Uses only Python stdlib — no openai or groq package needed.
    Supports both streaming and non-streaming chat.
    """

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        if not api_key or not api_key.strip():
            raise GroqAuthError("Groq API key is required.")
        self.api_key = api_key.strip()
        self.model   = model

    # ── public: one-shot chat ──────────────────────────────────────
    def chat(self, prompt: str, system: str = "") -> str:
        """
        Send a prompt and return the full response string.
        Blocks until complete.
        """
        messages = self._build_messages(prompt, system)
        payload  = {
            "model":    self.model,
            "messages": messages,
            "stream":   False,
        }
        data = self._post("/chat/completions", payload)
        return data["choices"][0]["message"]["content"].strip()

    # ── public: streaming chat ─────────────────────────────────────
    def chat_stream(self, prompt: str, system: str = "") -> Iterator[str]:
        """
        Stream the response token by token.
        Yields text chunks as they arrive.

        Usage:
            for chunk in client.chat_stream("analyse this data..."):
                print(chunk, end="", flush=True)
        """
        messages = self._build_messages(prompt, system)
        payload  = {
            "model":      self.model,
            "messages":   messages,
            "stream":     True,
            "max_tokens": 2048,
        }

        url  = GROQ_BASE_URL + "/chat/completions"
        body = json.dumps(payload).encode()
        req  = urllib.request.Request(
            url, data=body,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                for raw_line in resp:
                    line = raw_line.decode("utf-8").strip()

                    if not line or not line.startswith("data:"):
                        continue

                    data_str = line[5:].strip()   # strip "data: " prefix

                    if data_str == "[DONE]":
                        break

                    try:
                        obj   = json.loads(data_str)
                        delta = obj["choices"][0].get("delta", {})
                        text  = delta.get("content", "")
                        if text:
                            yield text
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

        except urllib.error.HTTPError as e:
            self._handle_http_error(e)
        except urllib.error.URLError as e:
            raise GroqAPIError(
                f"Network error reaching Groq API.\n"
                f"Check your internet connection.\nDetails: {e.reason}"
            ) from e

    # ── public: validate key ───────────────────────────────────────
    def validate_key(self) -> bool:
        """
        Quick check — sends a tiny request to verify the key works.
        Returns True if valid, raises GroqAuthError if not.
        """
        try:
            self.chat("Say OK", system="Reply with just the word OK.")
            return True
        except GroqAuthError:
            raise
        except Exception:
            return False

    # ── private helpers ────────────────────────────────────────────
    def _build_messages(self, prompt: str, system: str) -> list:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _post(self, path: str, payload: dict) -> dict:
        url  = GROQ_BASE_URL + path
        body = json.dumps(payload).encode()
        req  = urllib.request.Request(
            url, data=body,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            self._handle_http_error(e)
        except urllib.error.URLError as e:
            raise GroqAPIError(
                f"Network error: {e.reason}"
            ) from e

    def _handle_http_error(self, e: urllib.error.HTTPError):
        body = e.read().decode(errors="replace")
        try:
            detail = json.loads(body).get("error", {}).get("message", body)
        except Exception:
            detail = body

        if e.code == 401:
            raise GroqAuthError(
                "Invalid Groq API key OR key lacks model permission.\n\n"
                "How to fix:\n"
                "  1. Go to console.groq.com → API Keys\n"
                "  2. Click 'Create API Key'\n"
                "  3. IMPORTANT: Set 'Permissions' to 'Full Access'\n"
                "  4. Do NOT restrict to a specific project\n"
                "  5. Copy the new key (starts with gsk_...)\n\n"
                f"Groq error: {detail}"
            )
        elif e.code == 403:
            raise GroqAuthError(
                "API Key Forbidden (403) — Your account may have issues.\n\n"
                "Possible causes:\n"
                "  • API key has been revoked or is inactive\n"
                "  • Your Groq account has been suspended\n"
                "  • Account quota or limit exceeded\n"
                "  • API access has been disabled for your account\n\n"
                "How to fix:\n"
                "  1. Go to https://console.groq.com\n"
                "  2. Check if your account is active and has API access\n"
                "  3. Create a NEW API key\n"
                "  4. Make sure permissions are set to 'Full Access'\n"
                "  5. Copy the new key (starts with gsk_) and try again\n\n"
                f"Groq error details: {detail}"
            )
        elif e.code == 429:
            raise GroqRateLimitError(
                "Groq rate limit reached.\n"
                "Free tier: 30 requests/min, 14,400/day.\n"
                "Wait a moment and try again."
            )
        elif e.code == 404:
            raise GroqAPIError(
                f"Model '{self.model}' not found on Groq.\n"
                "Select a different model from the dropdown."
            )
        else:
            raise GroqAPIError(f"Groq API error {e.code}: {detail}")


# ── Shared prompt utilities ────────────────────────────────────────────────────
# These are identical to the Ollama versions so insights.py imports work
# with either backend by just changing the import line.

SYSTEM_PROMPT = """You are DataLens AI, an expert data analyst assistant embedded inside
a Python desktop analytics application. The user has uploaded a dataset and you have
been given its statistical summary. Your job is to:

1. Give clear, specific, actionable insights about the data.
2. Highlight anomalies, skewness, outliers, correlations, and data quality issues.
3. Suggest what the data might represent and what analyses make sense.
4. Be concise but thorough — bullet points are fine.
5. Use plain language — the user may not be a data scientist.

Do not make up numbers. Only reference what is in the summary provided.
"""


def build_analysis_prompt(df, question: str = "") -> str:
    """
    Build a rich prompt from dataframe stats + optional user question.
    Keeps token count reasonable by summarising rather than dumping raw data.
    """
    import numpy as np

    lines = [
        f"Dataset shape: {df.shape[0]:,} rows × {df.shape[1]} columns",
        f"Columns: {', '.join(df.columns.tolist())}",
        "",
    ]

    # numeric summary
    num = df.select_dtypes(include=np.number)
    if not num.empty:
        lines.append("=== NUMERIC COLUMNS ===")
        for col in num.columns:
            s = num[col].dropna()
            if len(s) == 0:
                continue
            lines.append(
                f"  {col}: mean={s.mean():.4g}, median={s.median():.4g}, "
                f"std={s.std():.4g}, min={s.min():.4g}, max={s.max():.4g}, "
                f"skew={s.skew():.2f}, nulls={df[col].isnull().sum()}"
            )

    # categorical summary
    cat = df.select_dtypes(include="object")
    if not cat.empty:
        lines.append("\n=== CATEGORICAL COLUMNS ===")
        for col in cat.columns:
            vc  = df[col].value_counts()
            top = vc.index[0] if len(vc) else "N/A"
            lines.append(
                f"  {col}: {df[col].nunique()} unique values, "
                f"top='{top}' ({vc.iloc[0] if len(vc) else 0}×), "
                f"nulls={df[col].isnull().sum()}"
            )

    # missing values
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        lines.append("\n=== MISSING VALUES ===")
        for col, n in missing.items():
            lines.append(f"  {col}: {n:,} missing ({n / len(df) * 100:.1f}%)")

    # top correlations
    if num.shape[1] >= 2:
        corr  = num.corr().abs()
        upper = corr.where(
            np.triu(np.ones(corr.shape), k=1).astype(bool)
        )
        top_pairs = upper.stack().sort_values(ascending=False).head(5)
        if not top_pairs.empty:
            lines.append("\n=== TOP CORRELATIONS ===")
            for (c1, c2), v in top_pairs.items():
                lines.append(f"  {c1} ↔ {c2}: r={v:.3f}")

    stat_summary = "\n".join(lines)

    if question.strip():
        return f"{stat_summary}\n\n=== USER QUESTION ===\n{question.strip()}"
    else:
        return (
            f"{stat_summary}\n\n=== TASK ===\n"
            "Please provide a comprehensive analysis of this dataset. "
            "Cover data quality, key patterns, notable statistics, "
            "correlations, and actionable recommendations."
        )