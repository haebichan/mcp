# vector_memory.py

from sentence_transformers import SentenceTransformer, util
import torch

THRESHOLD = 0.95

store = []  # In-memory vector store
model = SentenceTransformer("intfloat/e5-base-v2")

def check_similarity(query: str, threshold=THRESHOLD):
    query_embedding = model.encode(query, convert_to_tensor=True)
    if not store:
        return None
    embeddings_tensor = torch.stack([v['embedding'] for v in store])
    scores = util.cos_sim(query_embedding, embeddings_tensor)[0]
    best_idx = scores.argmax().item()
    if scores[best_idx] >= threshold:
        return store[best_idx]['text']
    return None

def add_to_vector_store(text: str):
    embedding = model.encode(text, convert_to_tensor=True)
    store.append({ "text": text, "embedding": embedding })
