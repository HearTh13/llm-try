import os
from google import genai
from google.genai import types
from openai import AsyncOpenAI

# Read configurations from environment variables
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower().strip()

# Resolve API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", os.getenv("LLM_API_KEY"))

# Resolve Model name
if LLM_PROVIDER == "openai":
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
else:
    # default to gemini
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash").strip()

# Initialize appropriate client
gemini_client = None
openai_client = None

if LLM_PROVIDER == "gemini":
    if GEMINI_API_KEY and GEMINI_API_KEY != "GANTI_DENGAN_API_KEY_GEMINI_KAMU_DISINI":
        # Menggunakan API v1beta karena system_instruction membutuhkan versi API beta atau yang lebih baru
        gemini_client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1beta'})
elif LLM_PROVIDER == "openai":
    if OPENAI_API_KEY and OPENAI_API_KEY != "GANTI_DENGAN_API_KEY_OPENAI_KAMU_DISINI":
        openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_response_async(prompt: str) -> str:
    if LLM_PROVIDER == "openai":
        if not openai_client:
            return "Error: OPENAI_API_KEY atau LLM_API_KEY belum di-setup dengan benar di environment."
        try:
            response = await openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error dari OpenAI API ({LLM_MODEL}): {str(e)}"
    else:
        # Default to Gemini
        if not gemini_client:
            return "Error: GEMINI_API_KEY atau LLM_API_KEY belum di-setup dengan benar di environment."
        try:
            response = await gemini_client.aio.models.generate_content(
                model=LLM_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="jawab jika pertanyaan hanya terkait dengan universitas sanata dharma"
                )
            )
            return response.text
        except Exception as e:
            return f"Error dari Gemini API ({LLM_MODEL}): {str(e)}"
