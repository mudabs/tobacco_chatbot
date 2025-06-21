import csv
import chromadb
from chromadb.utils import embedding_functions
from chromadb.errors import NotFoundError

client = chromadb.Client()

def get_or_create_collection(name="tobacco_faq"):
    try:
        return client.get_collection(name=name)
    except NotFoundError:
        return client.create_collection(name=name)

collection = get_or_create_collection()

def load_dataset():
    with open("data/tobacco_faq.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        questions = []
        answers = []
        ids = []
        for i, row in enumerate(reader):
            questions.append(row["question"])
            answers.append(row["answer"])
            ids.append(f"id{i}")
        collection.add(
            documents=answers,
            ids=ids,
            metadatas=[{"question": q} for q in questions]
        )

def query_vector_db(user_input):
    results = collection.query(
        query_texts=[user_input],
        n_results=3  # previously 1
    )
    documents = results.get("documents", [[]])[0]
    if not documents:
        return "No relevant info found."
    return "\n".join(documents)
