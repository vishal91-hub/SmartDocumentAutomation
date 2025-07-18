# graph/doc_creator.py

import os

from jinja2 import Environment, FileSystemLoader
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq.chat_models import ChatGroq
from dotenv import load_dotenv

load_dotenv()

TEMPLATE_DIR = os.path.join("data", "templates")

# Setup Groq LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="Llama3-8b-8192",   # or Mixtral-8x7b
    temperature=0.3,
    max_tokens=500,
)

def generate_document_from_template(template_name: str, user_inputs: dict) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_name)
    return template.render(**user_inputs)

def enhance_document_with_llm(doc_text: str) -> str:
    prompt = PromptTemplate.from_template(
        "Please polish and format the following document:\n\n{document}"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(document=doc_text)

def create_document(template_name: str, user_inputs: dict, use_llm=True) -> str:
    raw_text = generate_document_from_template(template_name, user_inputs)
    return enhance_document_with_llm(raw_text) if use_llm else raw_text
