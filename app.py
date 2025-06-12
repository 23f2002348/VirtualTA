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
#     "pillow",
#     "openai",
#     "google"
# ]



import os
from fastapi import FastAPI
from google import genai
from openai import OpenAI
from embed import helper
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
# Initialize clients once (adjust your init as needed)
genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# chromadb client init here
# ...
openai_client = OpenAI(
    api_key=os.getenv("AIPROXY_TOKEN"),
    base_url="https://aiproxy.sanand.workers.dev/openai/v1"
)

# === Request Model ===
class QueryRequest(BaseModel):
    query: str
    is_image: bool = False
    image_path: str | None = None

# === Helper Functions ===
def get_image_description(image_path):
    uploaded_file = genai.upload_file(image_path)
    response = genai.generate_content(
        model="gemini-1.5-pro",
        contents=[
            uploaded_file,
            "Describe this image in detail, including any text or objects."
        ],
    )
    return response.text

async def generate_answer(query, is_image=False, image_path=None, top_k=5):
    if is_image:
        if not image_path:
            raise ValueError("image_path is required for image-based queries.")
        query_text = get_image_description(image_path)
    else:
        query_text = query.strip()

    results = helper(query_text, top_k=top_k)
    docs = results.get("documents", [[]])[0]
    context = "\n\n".join(docs)

    prompt = f"""You are an expert assistant. Use the following context to answer the question below.

Context:
{context}

Question:
{query_text}

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

    return response.choices[0].message.content.strip()

# === POST Endpoint ===
@app.post("/")
async def handle_question(query_req: QueryRequest):
    answer = generate_answer(
        query=query_req.query,
        is_image=query_req.is_image,
        image_path=query_req.image_path
    )
    return {"answer": answer}