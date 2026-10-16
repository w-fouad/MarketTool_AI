
import os
import time
import pandas as pd
from google import genai


def analyze_market_gaps(data):
    if data is None or data.empty:
        return "No reviews available."

    data = data.copy()
    data["rating"] = pd.to_numeric(data["rating"], errors="coerce")

    low = data[data["rating"] <= 2]

    if low.empty:
        return "No low rated reviews found."

    low = low.head(100)

    text = ""

    for _, row in low.iterrows():
        t = str(row.get("review_text", "")).strip()

        if t and t.lower() != "nan":
            text += (
                f"App: {row.get('app_title', 'Unknown')} | "
                f"Rating: {row['rating']} | "
                f"Review: {t[:400]}\n"
            )

    if not text:
        return "No usable text."

    # Read API key from environment or Streamlit Secrets
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        return "Please set GEMINI_API_KEY in Streamlit Secrets."

    prompt = f"""
You are a market analyst. Analyze these low-rated reviews.

Please identify:
1. Main bugs and complaints
2. Missing features
3. Market opportunities
4. Three recommendations for a new app

Use only the reviews provided.
Mention any limitations in the data.

Reviews:
{text}
"""

    try:
        client = genai.Client(api_key=api_key)

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )

                if response.text:
                    return response.text

                return "Gemini returned an empty response."

            except Exception as e:
                error_message = str(e)

                # Retry only temporary service availability errors
                if "503" not in error_message or attempt == 2:
                    return f"AI analysis failed: {error_message}"

                time.sleep(2 * (attempt + 1))

    except Exception as e:
        return f"AI analysis failed: {e}"

    return "AI analysis could not be completed. Please try again."
