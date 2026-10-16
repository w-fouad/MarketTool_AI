import os
import pandas as pd
from google import genai

def analyze_market_gaps(reviews_df):
    if reviews_df is None or reviews_df.empty:
        return "No reviews available."

    reviews_df["rating"] = pd.to_numeric(reviews_df["rating"], errors="coerce")
    low = reviews_df[reviews_df["rating"] <= 2]

    if low.empty:
        return "No low rated reviews found. All ratings are good, try analyzing all reviews."
    
    # قللنا من 100 لـ 40 عشان ما يعلق
    low = low.head(40)

    text = ""
    for _, row in low.iterrows():
        t = str(row["review_text"]).strip()
        if t and t.lower() != "nan" and len(t) > 10:
            text += f"- {row['app_title']} ({row['rating']} stars): {t[:250]}\n"

    if not text:
        return "No usable text found."

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY")
        except:
            pass

    if not api_key:
        return "❌ Error: GEMINI_API_KEY not found. Go to Streamlit Settings > Secrets and add it."

    prompt = f"""
Analyze these {len(low)} bad reviews and give:
1. Top 5 bugs/complaints
2. Missing features users want
3. 2 market opportunities
4. 3 recommendations for a new app

Keep it short and in bullet points.

Reviews:
{text}
"""

    try:
        client = genai.Client(api_key=api_key)
        # غيرنا الموديل لـ 1.5-flash اسرع وما بعلق
        res = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        if res and res.text:
            return res.text
        else:
            return "Empty response from Gemini, try again."
    except Exception as e:
        # هون كان يعلق، هلا رح يطلعلك الخطأ بالزبط
        return f"❌ Gemini Error: {str(e)} \n\n Check: 1) API key is valid 2) You enabled Generative AI API in Google Cloud"
# import os
# import pandas as pd
# import streamlit as st
# from google import genai


# def analyze_market_gaps(data):
#     print("DEBUG 1: Analysis started", flush=True)

#     if data is None or data.empty:
#         return "No reviews available."

#     required_columns = {"rating", "review_text", "app_title"}
#     missing_columns = required_columns - set(data.columns)

#     if missing_columns:
#         return (
#             "Cannot analyze reviews. Missing columns: "
#             + ", ".join(sorted(missing_columns))
#         )

#     # Work on a copy so the original DataFrame is not changed.
#     df = data.copy()
#     df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

#     low = df[df["rating"] <= 2].head(100)

#     if low.empty:
#         return "No low-rated reviews found (ratings of 1 or 2)."

#     review_lines = []

#     for _, row in low.iterrows():
#         review = str(row["review_text"]).strip()

#         if review and review.lower() != "nan":
#             review_lines.append(
#                 f"App: {row['app_title']} | "
#                 f"Rating: {row['rating']} | "
#                 f"Review: {review[:400]}"
#             )

#     if not review_lines:
#         return "No usable text found in low-rated reviews."

#     review_text = "\n".join(review_lines)

#     # Get the API key from environment or Streamlit secrets.
#     api_key = os.getenv("GEMINI_API_KEY")

#     if not api_key:
#         try:
#             api_key = st.secrets.get("GEMINI_API_KEY")
#         except Exception:
#             api_key = None

#     if not api_key:
#         return (
#             "GEMINI_API_KEY is missing. "
#             "Add it to Streamlit Cloud Secrets or your local environment."
#         )

#     prompt = f"""
# You are a market research analyst.

# Analyze the following low-rated Google Play reviews.

# Provide:
# 1. Main bugs and customer complaints.
# 2. Missing features users appear to need.
# 3. Potential market gaps and opportunities.
# 4. Three practical recommendations for a new competing app.
# 5. Evidence from the reviews supporting each major finding.
# 6. Limitations: explain that conclusions are based only on the
#    supplied reviews and may not represent all users.

# Do not invent facts that are not supported by the reviews.
# Write the report in clear, structured Markdown.

# Reviews:
# {review_text}
# """

#     try:
#         print("DEBUG 2: Creating Gemini client", flush=True)
#         client = genai.Client(api_key=api_key)

#         print("DEBUG 3: Sending request to Gemini", flush=True)

#         response = client.interactions.create(
#             model="gemini-3.8-flash",
#             input=prompt,
#             timeout=60,
#         )

#         print("DEBUG 4: Gemini response received", flush=True)

#         result = getattr(response, "output_text", None)

#         if result and result.strip():
#             print("DEBUG 5: Analysis completed", flush=True)
#             return result.strip()

#         print("DEBUG 5: Empty response", flush=True)
#         return (
#             "Gemini returned an empty response. "
#             "Please try again."
#         )

#     except Exception as e:
#         error_message = f"{type(e).__name__}: {e}"
#         print(f"DEBUG ERROR: {error_message}", flush=True)

#         return (
#             "Gemini analysis failed.\n\n"
#             f"**Error:** `{error_message}`\n\n"
#             "Please check the terminal output, API key, model access, "
#             "and network connection."
#         )
