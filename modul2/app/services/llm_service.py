import os
from google import genai

# Konfigurasi API Key saat modul dimuat
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Menggunakan API v1 yang stabil untuk menghindari error 404 di endpoint v1beta
client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1'}) if GEMINI_API_KEY else None

async def generate_response_async(prompt: str) -> str:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "GANTI_DENGAN_API_KEY_GEMINI_KAMU_DISINI":
        return "Error: GEMINI_API_KEY belum di-setup dengan benar di environment."
    
    try:
        # Menggunakan model versi stabil terbaru dengan SDK google-genai
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error dari Gemini API: {str(e)}"