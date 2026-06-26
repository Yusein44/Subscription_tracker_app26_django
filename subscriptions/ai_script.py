import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def extract_invoice_data(file_path):
    try:
        print("[1] Качвам файла към Google...")
        sample_file = client.files.upload(file=file_path)
        
        prompt = """
        Ти си финансов AI асистент. Прочети тази фактура/касова бележка или лого.
        Върни ми САМО И ЕДИНСТВЕНО валиден JSON формат с тези ключове:
        "name": името на фирмата/услугата (напр. Netflix, AWS, Slack),
        "price": крайната цена (само число, напр. 150.00. Ако няма цена, върни 0),
        "currency": валутата (напр. USD, EUR, BGN. Ако няма, върни BGN)
        Не добавяй никакъв друг текст, обяснения или маркдаун!
        """
        
        print("[2] Анализирам документа с gemini-2.0-flash...")
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, sample_file]
        )
        
        response_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(response_text)
        
        print(f"[3] УСПЕХ! Намерих тези данни: {data}")
        return data
        
    except Exception as e:
        print(f"Грешка с AI: {e}")
        return None