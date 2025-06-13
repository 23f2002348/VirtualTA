# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "argparse",
#     "fastapi",
#     "httpx",
#     "markdownify",
#     "semantic_text_splitter",
#     "tqdm",
#     "uvicorn",
#     "python-dotenv",
#     "google-genai",
#     "google.generativeai"
#     "pillow",
#     "openai",
#     "google"
#     "base64"
#]


import base64
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from openai import OpenAI
from embed import helper
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import tempfile
import mimetypes
from urllib.parse import urlparse

load_dotenv()

app = FastAPI()
# Initialize clients once (adjust your init as needed)
#genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# chromadb client init here
# ...
openai_client = OpenAI(
    api_key=os.getenv("AIPROXY_TOKEN"),
    base_url="https://aiproxy.sanand.workers.dev/openai/v1"
)



from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key="your-random-session-key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # restrict to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
class CustomCORSHeadersMiddleware(BaseHTTPMiddleware):
       async def dispatch(self, request, call_next):
        # If it's a preflight request, return 200 directly
        if request.method == "OPTIONS":
            response = Response(status_code=200)
        else:
            response = await call_next(request)
        
        response.headers["Access-Control-Allow-Origin"] = "https://exam.sanand.workers.dev"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS, GET"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        return response


@app.options("/")
def preflight_handler(path: str):
    headers = {
        "Access-Control-Allow-Origin": "https://exam.sanand.workers.dev",
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Private-Network": "true",
    }
    return Response(status_code=200, headers=headers)
"""@app.options("/")
def options_handler():
    response = JSONResponse(content={"message": "Preflight OK"})
    response.headers["Access-Control-Allow-Origin"] = "https://exam.sanand.workers.dev"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response
"""
app.add_middleware(CustomCORSHeadersMiddleware)

# === Request Model ===
class QueryRequest(BaseModel):
    question: str
    image: str | None = None

# === Helper Functions ===
_image_description_cache = {}

import google.generativeai as genai

# Configure once at the start
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize model object
vision_model = genai.GenerativeModel("gemini-2.0-flash")

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    tmp_file.write(response.content)
    tmp_file.close()
    return tmp_file.name
def get_image_description(image_path):
    if image_path in _image_description_cache:
        return _image_description_cache[image_path]

    try:
        # Determine if image_path is a URL
        is_url = urlparse(image_path).scheme in ("http", "https")

        if is_url:
            response = requests.get(image_path)
            response.raise_for_status()
            image_bytes = response.content
            mime_type = response.headers.get("Content-Type", "image/jpeg")
        else:
            image_bytes = base64.b64decode(image_path)
            mime_type = "image/jpeg"  # Or infer from metadata if passed
             # Fallback

        image_part = {
            "mime_type": mime_type,
            "data": image_bytes,
        }

        response = vision_model.generate_content(
            [
                image_part,
                "First, present the text present in the image in double quotes. Then describe this image in detail, including any objects that may be of significance. Give more importance to the textual details present.",
            ]
        )

        desc = getattr(response, "text", "").strip()
        if not desc:
            raise ValueError("❌ No description generated.")

        _image_description_cache[image_path] = desc
        return desc

    except Exception as e:
        print("⚠️ Error in image description:", e)
        raise

def generate_answer(query, image_path=None, top_k=5):
    # If image + text both present, combine smartly
    query_text = query.strip()
    if image_path:
        image_desc = get_image_description(image_path)
        
        
        # Use image description only if it has meaningful length
        if image_desc and len(image_desc) > 15:
            if query_text:
                # Combine with some separator; tweak as needed
                combined_query = f"{query_text}\n\nImage Description: {image_desc}"
            else:
                combined_query = image_desc
        else:
            combined_query = query_text
    else:
        combined_query = query.strip()

    context="No question data provided"
    print(combined_query)
    if combined_query!="":
        
        results = helper(combined_query, top_k=top_k)
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        context = "\n\n".join(docs)
        links = []
        for meta in metadatas:
            url = meta.get("url")
            source = meta.get("source")
            if url and url.startswith("http") and url not in links:
                title = meta.get("topic_title")
                text = title if title else source
                links.append({
                    "url": url,
                    "text": text
                })

    prompt = f"""You are an expert assistant on the Tools in Data Science course of IITM BS Data Science degree. Use the following context to answer the question below.

Be precise and clear in your answers and make sure to be contextual and relative to the user's query. Give more importance to the text present in image queries if any and try to answer them.
Context:
{context}

Question:
{combined_query}

Answer:"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=512,
        temperature=0.3,
    )

    return {
        "answer": response.choices[0].message.content.strip(),
        "links": links
    }
# === POST Endpoint ===
@app.post("/")
async def handle_question(request: Request):
    # Check Content-Type header
    if request.headers.get("content-type") != "application/json":
        raise HTTPException(status_code=415, detail="Content-Type must be application/json")

    # Parse JSON body to your model
    query_req = await request.json()
    # Validate using Pydantic
     # if this is where you're getting query_req
    query_data = QueryRequest(**query_req)
    response = generate_answer(
        query=query_data.question,
        image_path=query_data.image
    )

    return response

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))  # Use PORT from Render
    uvicorn.run("app:app", host="0.0.0.0", port=port)
