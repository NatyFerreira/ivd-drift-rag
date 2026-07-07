import os, glob, json, re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def chunk_markdown(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    # Divide por seções ## (cada seção vira um chunk)
    parts = re.split(r'\n(?=## )', content)
    title_match = re.match(r'# (.+)', parts[0])
    doc_title = title_match.group(1) if title_match else os.path.basename(filepath)
    chunks = [p.strip() for p in parts if p.strip()]
    return doc_title, chunks

docs = []
for filepath in sorted(glob.glob("knowledge_base/*.md")):
    doc_title, chunks = chunk_markdown(filepath)
    for i, chunk in enumerate(chunks):
        docs.append({
            "source": os.path.basename(filepath),
            "doc_title": doc_title,
            "chunk_id": i,
            "text": chunk
        })

print(f"Total de chunks: {len(docs)}")

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
texts = [d["text"] for d in docs]
embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)  # produto interno = similaridade de cosseno (vetores normalizados)
index.add(np.array(embeddings).astype("float32"))

os.makedirs("rag_index", exist_ok=True)
faiss.write_index(index, "rag_index/faiss.index")
with open("rag_index/chunks.json", "w", encoding="utf-8") as f:
    json.dump(docs, f, ensure_ascii=False, indent=2)

print("Índice FAISS salvo em rag_index/")