import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import joblib
import tensorflow as tf
import faiss
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(title="Assistant de fiabilité IVD")

# ---------- Peça 1: détection d'anomalies ----------
autoencoder = tf.keras.models.load_model("models/autoencoder.keras")
scaler = joblib.load("models/scaler.pkl")
with open("models/config.json") as f:
    anomaly_config = json.load(f)
THRESHOLD = anomaly_config["threshold"]
N_FEATURES = anomaly_config["n_features"]

# ---------- Peça 2: RAG ----------
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
device = "mps" if torch.backends.mps.is_available() else "cpu"

embed_model = SentenceTransformer(EMBED_MODEL, device="cpu")
faiss_index = faiss.read_index("rag_index/faiss.index")
with open("rag_index/chunks.json", encoding="utf-8") as f:
    rag_chunks = json.load(f)

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
llm = AutoModelForCausalLM.from_pretrained(LLM_MODEL, dtype=torch.float32).to(device)


def rag_retrieve(query, k=5):
    q_emb = embed_model.encode([query], normalize_embeddings=True).astype("float32")
    scores, idxs = faiss_index.search(q_emb, k)
    return [{**rag_chunks[idx], "score": float(score)} for score, idx in zip(scores[0], idxs[0])]


def rag_answer(query, k=5):
    retrieved = rag_retrieve(query, k=k)
    context = "\n\n".join(f"[Source: {c['source']}]\n{c['text']}" for c in retrieved)
    system = (
        "Tu es un assistant qualité pour un système de diagnostic in vitro. "
        "Réponds à la question en te basant UNIQUEMENT sur le contexte fourni. "
        "Identifie le mécanisme spécifique mentionné dans le contexte qui explique "
        "la question posée — ne donne pas une explication générale si le contexte "
        "contient une cause précise. Sois concis (3-4 phrases maximum). "
        "Cite la source (nom du fichier) utilisée."
    )
    user = f"Contexte:\n{context}\n\nQuestion: {query}"
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]

    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
    ).to(device)
    output = llm.generate(**inputs, max_new_tokens=200, do_sample=False)
    response = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return response, retrieved


# ---------- Schemas ----------
class SensorReading(BaseModel):
    features: List[float] = Field(..., min_length=N_FEATURES, max_length=N_FEATURES)


class AnomalyResult(BaseModel):
    reconstruction_error: float
    is_anomaly: bool
    threshold: float


class Question(BaseModel):
    query: str
    k: int = 5


class RagSource(BaseModel):
    source: str
    score: float


class RagAnswer(BaseModel):
    answer: str
    sources: List[RagSource]


# ---------- Endpoints ----------
@app.get("/")
def root():
    return {"status": "ok", "service": "Assistant de fiabilité IVD"}


@app.post("/predict", response_model=AnomalyResult)
def predict(reading: SensorReading):
    X = np.array(reading.features).reshape(1, -1)
    X_scaled = scaler.transform(X)
    X_reconstructed = autoencoder.predict(X_scaled, verbose=0)
    error = float(np.mean(np.square(X_scaled - X_reconstructed)))
    return AnomalyResult(reconstruction_error=error, is_anomaly=error > THRESHOLD, threshold=THRESHOLD)


@app.post("/ask", response_model=RagAnswer)
def ask(question: Question):
    response, retrieved = rag_answer(question.query, k=question.k)
    sources = [RagSource(source=r["source"], score=r["score"]) for r in retrieved]
    return RagAnswer(answer=response, sources=sources)