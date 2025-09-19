import os
import io
import json
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

def configure_gemini():
    """Configures the Gemini API with the key from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in a .env file.")
    genai.configure(api_key=api_key)

# Initialize Gemini at startup
configure_gemini()

# ===============================
# Pitch Deck PDF Processing
# ===============================
def pdf_to_images(pdf_path: str):
    """Convert PDF to a list of PIL images (one per page)."""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        images.append(image)
    doc.close()
    return images


def generate_table_of_contents(page_images: list):
    """Stage 1: Use Gemini to generate TOC."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = """
    You are a document analysis expert. Your task is to create a table of contents for this pitch deck.
    Analyze all the pages provided and identify the main sections.
    Return a JSON object where keys are the main topics (e.g., "Problem", "Solution", "Team", "Market_Size", "Financials", "Competition", "Traction", "Ask") and values are a list of page numbers where that topic is discussed.
    Page numbers should be 1-based.
    Example response: {"Problem": [2], "Solution": [3, 4], "Team": [5]}
    """
    content = [prompt] + page_images
    response = model.generate_content(content)
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_response)


def extract_topic_data(topic: str, page_images: list):
    """Stage 2: Extract topic-specific data."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    You are a startup analyst. Analyze the following pages which are known to be about the topic: '{topic}'.
    Synthesize all information from these pages to provide a complete and detailed summary for this section.
    Present the information in a clear, well-structured format. If it's a list (like team members or competitors), use bullet points.
    Be very specific when generating the response, dont include texts like 'Here is the breakdown' or 'being an AI agent'. Always refer
    to the {topic} and provide the accureate responses. 
    """
    content = [prompt] + page_images
    response = model.generate_content(content)
    return response.text


def generate_embeddings(text: str, task_type: str = "RETRIEVAL_DOCUMENT"):
    """Generate embeddings for text."""
    model = "models/text-embedding-004"
    embedding = genai.embed_content(model=model, content=text, task_type=task_type)
    return embedding["embedding"]

def json_to_markdown(data: dict) -> str:
    """Convert dict to markdown string."""
    markdown_string = ""
    for key, value in data.items():
        markdown_string += f"## {key.replace('_', ' ').title()}\n\n{value}\n\n"
    return markdown_string

def process_pitch_deck(pdf_path: str):
    """Pipeline for PDF pitch deck analysis."""
    os.makedirs("results", exist_ok=True)

    all_page_images = pdf_to_images(pdf_path)
    toc = generate_table_of_contents(all_page_images)

    final_structured_data = {}
    for topic, page_nums in toc.items():
        topic_images = [all_page_images[p - 1] for p in page_nums if 0 < p <= len(all_page_images)]
        if not topic_images:
            continue
        extracted_data = extract_topic_data(topic, topic_images)
        final_structured_data[topic] = extracted_data

    # Save structured JSON
    with open("results/Consolidated_result.json", "w") as f:
        json.dump(final_structured_data, f, indent=2)

    # Save Markdown
    markdown_content = json_to_markdown(final_structured_data)
    with open("results/analysis_results.md", "w") as f:
        f.write(markdown_content)

    # Embeddings
    embeddings = generate_embeddings(json.dumps(final_structured_data, indent=2))

    return {
        "toc": toc,
        "analysis": final_structured_data,
        "embedding_dimension": len(embeddings)
    }
