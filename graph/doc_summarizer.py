# graph/doc_summarizer.py

import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from utils.pdf_utils import extract_text_from_pdf
from utils.text_cleaner import clean_text
from dotenv import load_dotenv

load_dotenv()  # Load GROQ_API_KEY from .env

def summarize_text(text: str) -> str:
    """
    Uses a Groq LLM to summarize the given document text.
    """
    cleaned = clean_text(text)

    prompt = PromptTemplate.from_template(
        "Summarize the following document, highlighting important terms, responsibilities, dates, and signature requirements:\n\n{doc_text}"
    )

    llm = ChatGroq(
        model="Llama3-8b-8192",  # Or use llama3-8b-8192
        temperature=0.4,
        max_tokens=300,
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    summary = chain.run(doc_text=cleaned)
    return summary

def summarize_document(file_path: str) -> str:
    """
    Read and summarize a document (PDF or text).
    """
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        full_text = extract_text_from_pdf(file_path)
    elif ext == ".txt":
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return summarize_text(full_text)
