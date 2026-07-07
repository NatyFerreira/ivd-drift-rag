import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import faiss

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

device = "mps" if torch.backends.mps.is_available() else "cpu"

print("Chargement du modèle d'embeddings...")
embed_model = SentenceTransformer(EMBED_MODEL, device="cpu")

print("Chargement de l'index FAISS...")
index = faiss.read_index("rag_index/faiss.index")
with open("rag_index/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

print("Chargement du LLM (peut prendre un moment la 1ère fois)...")
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
llm = AutoModelForCausalLM.from_pretrained(LLM_MODEL, dtype=torch.float32).to(device)

def retrieve(query, k=3):
    q_emb = embed_model.encode([query], normalize_embeddings=True).astype("float32")
    scores, idxs = index.search(q_emb, k)
    return [{**chunks[idx], "score": float(score)} for score, idx in zip(scores[0], idxs[0])]


def build_prompt(query, retrieved_chunks):
    context = "\n\n".join(f"[Source: {c['source']}]\n{c['text']}" for c in retrieved_chunks)
    system = (
        "Tu es un assistant qualité pour un système de diagnostic in vitro. "
        "Réponds à la question en te basant UNIQUEMENT sur le contexte fourni. "
        "Identifie le mécanisme spécifique mentionné dans le contexte qui explique "
        "la question posée — ne donne pas une explication générale si le contexte "
        "contient une cause précise. Sois concis (3-4 phrases maximum). "
        "Cite la source (nom du fichier) utilisée."
    )
    user = f"Contexte:\n{context}\n\nQuestion: {query}"
    return system, user


def answer(query, k=3):
    retrieved = retrieve(query, k=k)
    system, user = build_prompt(query, retrieved)
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True
    ).to(device)

    output = llm.generate(**inputs, max_new_tokens=200, do_sample=False)
    response = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return response, retrieved


if __name__ == "__main__":
    q = "Pourquoi le batch 1 a-t-il autant de fausses alertes ?"
    resp, retrieved = answer(q, k=5)
    print("\nSources récupérées:")
    for r in retrieved:
        print(f"  - {r['source']} (score={r['score']:.3f})")
    print("\nRéponse:\n", resp)