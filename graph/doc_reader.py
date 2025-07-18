import os
import json
import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq  # ✅ Import Groq chat model

from utils.pdf_utils import extract_text_from_pdf
from utils.text_cleaner import clean_text
from dotenv import load_dotenv

load_dotenv()

def extract_metadata_with_llm(text: str) -> dict:
    """
    Use Groq LLM to extract structured metadata from the document.
    """
    prompt = PromptTemplate.from_template("""
You are an assistant that helps extract structured metadata from formal documents.

Please extract the following fields from the document below:

1. **Document Title** – The formal title of the document (e.g., Agreement Name)
2. **Parties involved** – List the entities or individuals participating (e.g., employer, employee)
3. **Date fields** – Extract all dates and annotate their meaning (e.g., start date, due date, signature date)
4. **Signature Sections** – Identify all lines or phrases that indicate a need for a signature (e.g., “Signature: ________”, “Signed by”, etc.). Include the surrounding sentence or clause if applicable.

Document:
{doc_text}

Return the extracted information in the following JSON format:
{{
  "Document Title": "...",
  "Parties involved": ["...", "..."],
  "Date fields": {{
    "Start Date": "...",
    "End Date": "...",
    ...
  }},
  "Signature Sections": [
    "Signature: ______________________ (Employer)",
    "Signed by the Contractor on page 4",
    ...
  ]
}}
""")

    llm = ChatGroq(
        model_name="Llama3-8b-8192",
        temperature=0.3,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    llm_output = chain.run(doc_text=clean_text(text))

    # ✅ Safely extract JSON from LLM output
    try:
        json_str_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
        if not json_str_match:
            raise ValueError("No valid JSON found in LLM response.")

        json_str = json_str_match.group()
        metadata = json.loads(json_str)
    except Exception as e:
        print("❌ Failed to parse metadata JSON:", e)
        metadata = {}

    return metadata


def read_and_extract_metadata(file_path: str) -> dict:
    """
    Load text from PDF/TXT and extract metadata using LLM.
    """
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported file format")

    return extract_metadata_with_llm(text)
