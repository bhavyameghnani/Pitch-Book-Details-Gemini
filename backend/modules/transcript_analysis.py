
import re, os, json
from PIL import Image
import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

def configure_gemini():
    """Configures the Gemini API with the key from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in a .env file.")
    genai.configure(api_key=api_key)

# Initialize Gemini at startup
configure_gemini()

def analyze_transcript_with_ai(transcript_content: str) -> List[Dict]:
    """Analyzes transcript text with Gemini."""
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f'''
    You are an expert AI analyst. Analyze the following transcript of a company.
    Identify and extract the following information:
    - Company / startup_name: The name of the startup.
    - summary: key insights of the talk.
    - founders: Information about the founders.
    - problem_statement: The problem the startup is solving.
    - solution: The solution they offer.
    - funding: A dictionary with 'raised' and 'seeking' amounts.
    - market: A dictionary with 'size' and 'traction' details.
    - risks: Potential risks or challenges mentioned or implied.
    - key_insights: Unique advantages or important takeaways from the pitch.

    Respond with ONLY a valid JSON array of objects.
    Do not include any explanatory text before or after the JSON.

    Transcript:
    ---
    {transcript_content}
    ---
    '''

    response = model.generate_content(prompt)
    text_response = response.text

    # Extract JSON if wrapped in ```json ```
    json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text_response)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = text_response

    return json.loads(json_str)




# prompt = f'''
    # You are an expert AI analyst. Analyze the following transcript of a startup pitch competition.
    # Identify each startup that pitches and for each one, extract the following information:
    # - startup_name: The name of the startup.
    # - summary: A concise summary of the business.
    # - founders: Information about the founders.
    # - problem_statement: The problem the startup is solving.
    # - solution: The solution they offer.
    # - funding: A dictionary with 'raised' and 'seeking' amounts.
    # - market: A dictionary with 'size' and 'traction' details.
    # - risks: Potential risks or challenges mentioned or implied.
    # - key_insights: Unique advantages or important takeaways from the pitch.

    # Respond with ONLY a valid JSON array of objects, where each object represents a startup.
    # Do not include any explanatory text before or after the JSON.

    # Transcript:
    # ---
    # {transcript_content}
    # ---
    # '''