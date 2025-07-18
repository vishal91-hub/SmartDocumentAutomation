# # test_doc_creator.py

# from graph.doc_creator import create_document

# doc = create_document(
#     template_name="employment_offer.txt",
#     user_inputs={
#         "recipient_name": "Neha Sharma",
#         "role": "Software Engineer",
#         "start_date": "1st August 2025",
#         "salary": "12,00,000",
#         "location": "Bangalore"
#     }
# )

# print("📄 Generated Document:\n")
# print(doc)

# from graph.doc_summarizer import summarize_document

# summary = summarize_document("data/uploads/employment.pdf")
# print(summary)


from graph.doc_reader import read_and_extract_metadata

# Provide the path to a test PDF or TXT document
file_path = "data/uploads/employment.pdf"  # Make sure this file exists

result = read_and_extract_metadata(file_path)

print("\n--- Extracted Metadata ---\n")
print(result)