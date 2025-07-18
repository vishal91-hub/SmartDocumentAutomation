# main.py

import streamlit as st
import json
import os
import fitz  # PyMuPDF
from graph.esign_flow import build_esign_graph
from utils.file_utils import save_uploaded_file

st.set_page_config(page_title="Smart Document E-Sign Workflow", layout="wide")
st.title("📄 Smart Document Automation and E-Sign")

# Step 1: Choose document source
source = st.radio("Choose document source:", ["Generate New Document", "Upload Existing Document"])

doc_text = ""
metadata = None

# 📄 Option 1: Generate New Document from Template
if source == "Generate New Document":
    template_name = st.sidebar.text_input("Template Name", value="nda_template.j2.txt")

    user_data_input = st.sidebar.text_area(
        "User Data (JSON)",
        height=300,
        value='{\n'
              '  "party1": {\n'
              '    "name": "Alice",\n'
              '    "address": "123 Main St, NY"\n'
              '  },\n'
              '  "party2": {\n'
              '    "name": "Bob",\n'
              '    "address": "456 Park Ave, LA"\n'
              '  },\n'
              '  "date": "July 17, 2025"\n'
              '}'
    )

    try:
        user_data = json.loads(user_data_input)
        metadata = {
            "template_name": template_name,
            "user_data": user_data
        }
    except Exception as e:
        st.error(f"❌ Invalid JSON in User Data: {e}")

# 📤 Option 2: Upload Existing Document
elif source == "Upload Existing Document":
    uploaded_file = st.file_uploader("Upload document (PDF or TXT)", type=["pdf", "txt"])
    if uploaded_file:
        file_path = save_uploaded_file(uploaded_file)
        metadata = {
            "uploaded_file": file_path
        }

# 🧠 Run Workflow
if metadata and st.button("🔁 Run Workflow"):
    esign_graph = build_esign_graph()

    # Read uploaded file content if applicable
    if "uploaded_file" in metadata:
        uploaded_path = metadata["uploaded_file"]
        ext = os.path.splitext(uploaded_path)[1].lower()

        try:
            if ext == ".pdf":
                with fitz.open(uploaded_path) as pdf:
                    doc_text = ""
                    for page in pdf:
                        doc_text += page.get_text()
            elif ext == ".txt":
                with open(uploaded_path, "r", encoding="utf-8") as f:
                    doc_text = f.read()
            else:
                st.warning("Unsupported file format. Please upload PDF or TXT.")
                doc_text = ""
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
            doc_text = ""
    else:
        doc_text = ""

    # Prepare LangGraph state
    state = {
        "doc_text": doc_text,
        "metadata": metadata,
        "signed": False
    }

    try:
        result = esign_graph.invoke(state)
        st.success("✅ Workflow completed!")

        # 📄 Document Preview
        st.subheader("📄 Document Preview")
        st.text_area("Generated Document", result.get("doc_text", "No document generated."), height=300)

        # 🧠 Summary
        st.subheader("🧠 Summary")
        st.write(result.get("summary", "No summary generated."))

        # 📑 Metadata
        st.subheader("📑 Extracted Metadata")
        st.json(result.get("metadata", {}))

        # ✍️ Signature Info
        st.subheader("✍️ Signature Section")
        with st.form("signature_form"):
            signer1 = st.text_input("Signer Name (Party 1)")
            signer2 = st.text_input("Signer Name (Party 2)")
            sig_date = st.date_input("Signature Date")
            submitted = st.form_submit_button("Submit Signature Info")
            if submitted:
                st.success("🖊️ Signature info submitted.")

        # ✅ Download Button OUTSIDE form
        if result.get("doc_text"):
            st.download_button(
                "⬇️ Download Document",
                result["doc_text"].encode("utf-8"),
                file_name="final_document.txt",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"❌ Error during workflow: {e}")
