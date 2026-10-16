from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import os

from pydantic import BaseModel

# pyrefly: ignore [missing-import]
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

app = FastAPI() 

class ItemBody(BaseModel):
    request:str

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

PRODUCTS = [
  {
    "name": "Sony BRAVIA W830K",
    "model": "KD-32W830K",
    "sizeInches": 32,
    "displayType": "LED LCD",
    "resolution": "1366 × 768",
    "processor": "X-Reality PRO",
    "features": ["HDR10", "HLG", "Google TV", "50 Hz panel"]
  },
  {
    "name": "Sony BRAVIA W880K",
    "model": "KD-43W880K",
    "sizeInches": 43,
    "displayType": "LED LCD",
    "resolution": "1920 × 1080",
    "processor": "X-Reality PRO",
    "features": ["Live Colour", "HDR10", "HLG", "50 Hz panel"]
  },
  {
    "name": "Sony BRAVIA 3",
    "model": "K-43S30",
    "sizeInches": 43,
    "displayType": "LED LCD",
    "resolution": "3840 × 2160",
    "processor": "4K HDR Processor X1",
    "features": ["Triluminos Pro", "Google TV", "X-Balanced speakers"]
  },
  {
    "name": "Sony BRAVIA 3",
    "model": "K-50S30",
    "sizeInches": 50,
    "displayType": "LED LCD",
    "resolution": "3840 × 2160",
    "processor": "4K HDR Processor X1",
    "features": ["Triluminos Pro", "Google TV", "Game Menu"]
  },
  {
    "name": "Sony BRAVIA XR X90L",
    "model": "XR-55X90L",
    "sizeInches": 55,
    "displayType": "Full Array LED LCD",
    "resolution": "3840 × 2160",
    "processor": "Cognitive Processor XR",
    "features": ["Local dimming", "HDR", "Google TV"]
  },
  {
    "name": "Sony BRAVIA 7",
    "model": "K-65XR70",
    "sizeInches": 65,
    "displayType": "Mini LED LCD",
    "resolution": "3840 × 2160",
    "processor": "XR Processor",
    "features": ["XR Backlight Master Drive", "Acoustic Multi-Audio", "Google TV"]
  },
  {
    "name": "Sony BRAVIA 9",
    "model": "K-75XR90",
    "sizeInches": 75,
    "displayType": "Mini LED LCD",
    "resolution": "3840 × 2160",
    "processor": "XR Processor",
    "features": ["XR Backlight Master Drive", "Acoustic Multi-Audio+", "Google TV"]
  },
  {
    "name": "Sony BRAVIA 5",
    "model": "K-98XR55A",
    "sizeInches": 98,
    "displayType": "Mini LED LCD",
    "resolution": "3840 × 2160",
    "processor": "XR Processor",
    "features": ["XR Backlight Master Drive", "Acoustic Multi-Audio", "Google TV"]
  },
  {
    "name": "Sony BRAVIA 8",
    "model": "K-55XR80",
    "sizeInches": 55,
    "displayType": "OLED",
    "resolution": "3840 × 2160",
    "processor": "XR Processor",
    "features": ["Self-lit pixels", "HDR", "Google TV"]
  },
  {
    "name": "Sony BRAVIA 8 II",
    "model": "K-65XR80M2",
    "sizeInches": 65,
    "displayType": "QD-OLED",
    "resolution": "3840 × 2160",
    "processor": "XR Processor",
    "features": ["Acoustic Surface Audio+", "4K/120 Hz input", "VRR", "Google TV"]
  }
]

def format_product(p):
    return (
        f"- {p['name']} ({p['model']}): {p['sizeInches']} inch, {p['displayType']}, "
        f"{p['resolution']}, {p['processor']}, features: {', '.join(p['features'])}"
    )

product_list = "\n".join(format_product(p) for p in PRODUCTS)

SYSTEM_PROMPT = f"""You are a helpful TV sales assistant.

You may ONLY recommend TVs from this product list:
{product_list}

Rules:
- Never recommend, mention or compare with any TV that is not in the list above.
- Only use the specs given in the list. Do not make up prices, specs or features.
- When recommending, give the exact name and model number from the list.
- If no TV in the list fits the customer's need, say so honestly.
- If the question is not about these TVs, politely say you can only help with TV recommendations."""

@app.get("/")
def read_root():
    print("Working like a fine wine")
    return {"status": "ok"}

@app.post("/chat")
def chat(body: ItemBody):
    response = client.chat.completions.create(
        model="gpt-4.1",
        max_tokens = 250,
        temperature = 0.2,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": body.request},
        ]
    )
    answer = response.choices[0].message.content
    print(answer)
    return {"answer": answer}

@app.post("/stream")
def generate_tokens(user_request: str):
    stream = client.chat.completions.create(
        model="gpt-4.1",
        max_tokens = 250,
        temperature = 0.2,
        stream = True,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_request},
        ]
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        token = chunk.choices[0].delta.content
        if token:
            print(token, end="", flush=True)
            yield token

    # for event in stream :
    #   print(event)
    

@app.post("/chat/stream")
def chat_stream(body: ItemBody):
    return StreamingResponse(generate_tokens(body.request), media_type="text/plain")

