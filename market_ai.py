
import os
import time
import pandas as pd
from google import genai


def analyze_market_gaps(data):
    if data is None or data.empty:
        return "No reviews available."

    data = data.copy()
    data["rating"] = pd.to_numeric(data["rating"], errors="coerce")

    # Analyze low-rated reviews only
    low = data[data["rating"] <= 2]

    if low.empty:
        return "No low-rated reviews found (ratings 1 or 2)."

    low = low.head(100)
    reviews = []

    for _, row in low.iterrows():
        review_text = str(row.get("review_text", "")).strip()

        if review_text and review_text.lower() != "nan":
            reviews.append(
                f"App: {row.get('app_title', 'Unknown')} | "
                f"Rating: {row['rating']} | "
                f"Review: {review_text[:400]}"
            )

    if not reviews:
        return "No usable review text found."

    reviews_text = "\n".join(reviews)

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
You are a market research analyst.

Analyze these low-rated Google Play reviews and identify:

1. Main bugs and customer complaints
2. Missing features
3. Market gaps and opportunities
4. Three practical recommendations for a new app
5. Limitations of this analysis

Use only the review data provided. Do not invent facts.

Reviews:
{reviews_text}
"""

    try:
        client = genai.Client(api_key=api_key)

        for attempt in range(3):
            try:
                response = client.interactions.create(
                    model="gemini-3.8-flash",
                    input=prompt
                )

                result = getattr(response, "output_text", None)

                if result:
                    return result

                return "Gemini returned an empty response."

            except Exception as e:
                error_message = str(e)
                is_temporary = (
                    "503" in error_message
                    or "UNAVAILABLE" in error_message
                )

                if not is_temporary or attempt == 2:
                    return (
                        "Gemini analysis failed. "
                        f"Technical details: {error_message}"
                    )

                time.sleep(2 * (attempt + 1))

    except Exception as e:
        return f"Gemini client error: {e}"

    return "AI analysis could not be completed. Please try again."
