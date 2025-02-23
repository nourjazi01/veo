from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"  # Lightweight and efficient
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embeddings(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    # Use mean pooling to get sentence embeddings
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings

def compute_similarity(text1, text2):
    embeddings = get_embeddings([text1, text2])
    similarity = cosine_similarity(embeddings[0].numpy().reshape(1, -1), embeddings[1].numpy().reshape(1, -1))
    return similarity[0][0]

def is_match(text1, text2, threshold=0.8):
    similarity_score = compute_similarity(text1, text2)
    print(f"Similarity Score: {similarity_score:.2f}")
    return similarity_score >= threshold


text1 = "Data Analyst"
text2 = "Data Science"

if is_match(text1, text2, threshold=0.8):
    print("The texts are a match!")
else:
    print("The texts are not a match.")