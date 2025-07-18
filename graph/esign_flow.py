# graph/esign_flow.py

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableLambda

from graph.doc_creator import create_document
from graph.doc_summarizer import summarize_document
from graph.doc_reader import read_and_extract_metadata
from typing import TypedDict, Optional


class DocState(TypedDict):
    doc_text: str
    metadata: Optional[dict]
    signed: Optional[bool]
    summary: Optional[str]


# New decision node for entry
def start_flow(state: DocState) -> DocState:
    """Decide whether to generate a new document or use uploaded."""
    if state["metadata"].get("use_uploaded_file", False):
        print("📤 Using uploaded document...")
        with open(state["metadata"]["uploaded_file_path"], "r", encoding="utf-8") as f:
            doc_text = f.read()

        return {
            "doc_text": doc_text,
            "metadata": state["metadata"],
            "signed": False
        }
    else:
        # Let it go to create_doc node
        return state


def document_creator_node(state: DocState) -> DocState:
    metadata = state.get("metadata", {})

    # If it's a template-based generation
    if "template_name" in metadata and "user_data" in metadata:
        template_name = metadata["template_name"]
        user_data = metadata["user_data"]

        doc_text = create_document(template_name, user_data, use_llm=True)

        return {
            "doc_text": doc_text,
            "metadata": metadata,
            "signed": False
        }

    # If it's an uploaded document, just pass through the existing text
    elif state.get("doc_text"):
        return {
            "doc_text": state["doc_text"],
            "metadata": metadata,
            "signed": False
        }

    else:
        raise ValueError("Insufficient data to generate or use document.")



def summarizer_node(state: DocState) -> DocState:
    print("📄 Summarizing document...")
    doc_path = "data/uploads/temp_doc.txt"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(state["doc_text"])

    summary = summarize_document(doc_path)
    print("✅ Summary:", summary)

    return {
        "doc_text": state["doc_text"],
        "metadata": state.get("metadata"),
        "signed": state.get("signed", False),
        "summary": summary
    }


def metadata_extractor_node(state: DocState) -> DocState:
    print("🔍 Extracting metadata...")
    doc_path = "data/uploads/temp_doc.txt"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(state["doc_text"])

    metadata = read_and_extract_metadata(doc_path)

    return {
        "doc_text": state["doc_text"],
        "metadata": metadata,
        "signed": state.get("signed", False)
    }


def build_esign_graph():
    builder = StateGraph(DocState)
    builder.set_entry_point("start")

    # Nodes
    builder.add_node("start", RunnableLambda(start_flow))
    builder.add_node("create_doc", RunnableLambda(document_creator_node))
    builder.add_node("summarize_doc", RunnableLambda(summarizer_node))
    builder.add_node("extract_metadata", RunnableLambda(metadata_extractor_node))

    # Edges
    builder.add_conditional_edges(
        "start",
        lambda state: "create_doc" if not state["metadata"].get("use_uploaded_file", False) else "summarize_doc"
    )

    builder.add_edge("create_doc", "summarize_doc")
    builder.add_edge("summarize_doc", "extract_metadata")
    builder.add_edge("extract_metadata", END)

    return builder.compile()
