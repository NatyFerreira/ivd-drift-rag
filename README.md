# Assistant de fiabilité IVD

Prototype démontrant deux approches d'IA appliquées à la fiabilité de systèmes de
diagnostic in vitro (IVD) : détection de dérive par deep learning, et assistance
qualité par RAG (Retrieval-Augmented Generation) avec un LLM local.

Projet développé pour explorer concrètement les compétences demandées dans les
offres data & IA appliquées au biomédical : deep learning, détection d'anomalies,
LLM, RAG, embeddings, bases vectorielles — au-delà de ce que couvre un cursus
Data Engineering standard.

## Architecture
┌─────────────────────┐
                │   FastAPI (api.py)   │
                └──────────┬───────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                  │
┌─────────▼──────────┐          ┌────────────▼───────────┐
│   POST /predict      │          │      POST /ask          │
│  Détection dérive    │          │   RAG qualité IVD        │
└─────────┬──────────┘          └────────────┬───────────┘
          │                                  │
┌─────────▼──────────┐          ┌────────────▼───────────┐
│  Autoencoder (TF)   │          │ Embeddings multilingues │
│  + StandardScaler   │          │ + Index FAISS            │
│                      │          │ + LLM local (Qwen2.5)    │
└─────────┬──────────┘          └────────────┬───────────┘
          │                                  │
┌─────────▼──────────┐          ┌────────────▼───────────┐
│ Gas Sensor Drift     │          │  knowledge_base/*.md      │
│ Dataset (UCI)         │          │  (procédures QC types)    │
└─────────────────────┘          └───────────────────────┘

## Composant 1 — Détection de dérive (deep learning)

**Dataset** : [UCI Gas Sensor Array Drift Dataset](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset+at+different+concentrations)
— 13 910 mesures, 16 capteurs chimiques, 10 batches sur 36 mois. Choisi comme
proxy réaliste de dérive instrumentale : le phénomène statistique (dérive
progressive + événements ponctuels) est identique à celui d'un analyseur IVD,
même si le domaine d'origine diffère.

**Approche** : autoencoder non supervisé (128 → 64 → 16 → 64 → 128, Keras/TensorFlow).
Entraîné à reconstruire ses propres entrées ; l'erreur de reconstruction sert de
score d'anomalie. Approche non supervisée choisie délibérément : dans un contexte
réel de monitoring IVD, on n'a généralement pas de label "ceci est une anomalie"
fiable a priori.

**Seuil** : percentile 95 de l'erreur de reconstruction, plutôt que moyenne +
N écarts-types. La distribution des erreurs est fortement asymétrique (outliers
extrêmes visibles au boxplot), ce qui rend moyenne/écart-type non fiables — les
outliers eux-mêmes déforment le seuil censé les capturer.

**Validation** : triangulation par PCA (visualisation de la dérive dans le temps),
boxplot par batch (distinction entre anomalies ponctuelles et dérive systémique),
et superposition anomalies détectées / PCA (cohérence visuelle confirmée).

**Limite identifiée et documentée** : les batches sous-représentés dans le
dataset (peu d'échantillons) montrent un taux de faux positifs plus élevé,
car l'autoencoder les a moins vus à l'entraînement. Ce biais est explicitement
documenté dans `knowledge_base/05_gestion_alertes.md` et correctement identifié
par le RAG (voir exemples plus bas).

## Composant 2 — RAG qualité (LLM local)

**Base de connaissances** : 6 documents markdown couvrant des procédures QC
standard du secteur (règles de Westgard, protocole de réponse à une dérive,
critères de recalibration, types d'erreurs analytiques, gestion des alertes,
documentation d'incidents). Contenu rédigé à partir de connaissances générales
du domaine, structuré en chunks par section (`##`) pour une recherche précise.

**Pipeline** :
1. Embeddings multilingues (`paraphrase-multilingual-MiniLM-L12-v2`) — choisi
   pour la qualité de la recherche sémantique en français.
2. Index vectoriel FAISS (`IndexFlatIP`, similarité cosinus).
3. LLM local `Qwen2.5-1.5B-Instruct` (Hugging Face Transformers), génération
   déterministe (`do_sample=False`) pour maximiser la fidélité au contexte
   récupéré plutôt que la créativité.

**Choix "100% local"** : aucune dépendance à une API payante externe — tourne
entièrement sur Apple Silicon (MPS), pertinent pour un contexte où la
confidentialité des données de diagnostic est critique.

## Stack technique

| Domaine | Outils |
|---|---|
| Deep learning | TensorFlow/Keras, scikit-learn |
| API | FastAPI, Pydantic |
| RAG | sentence-transformers, FAISS, Hugging Face Transformers |
| LLM | Qwen2.5-1.5B-Instruct (local, MPS) |
| Data | pandas, numpy, matplotlib |

## Installation

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install tensorflow scikit-learn pandas matplotlib fastapi uvicorn pydantic \
            sentence-transformers faiss-cpu transformers torch

python3 build_index.py      # construit l'index FAISS à partir de knowledge_base/
uvicorn api:app              # démarre le service (les deux endpoints)
```

Interface interactive : `http://127.0.0.1:8000/docs`

## Exemples d'utilisation

**Détection d'anomalie :**
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [...]}'  # vecteur de 128 features
```

**Question qualité (RAG) :**
```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Pourquoi le batch 1 a-t-il autant de fausses alertes ?", "k": 5}'
```

Réponse type : *"Le batch 1 a autant de fausses alertes probablement parce
qu'il inclut des capteurs peu représentés, ce qui entraîne plus de faux
positifs... Il serait judicieux d'ajuster les seuils sur des données
historiques représentatives plutôt que sur un échantillon trop restreint."*

## Problèmes techniques résolus

- **Segfault TensorFlow sur Python 3.13 (Anaconda)** : conflit de bibliothèques
  natives dans l'environnement conda. Résolu par un venv Python 3.11 isolé.
- **Segfault PyTorch/Transformers (float16 sur MPS)** : instabilité du support
  Metal pour float16 avec des modèles de cette taille. Résolu en forçant
  `dtype=torch.float32`.
- **Segfault au chargement combiné FAISS + PyTorch** : conflit OpenMP dupliqué
  (le même type de problème que le premier, cause différente). Résolu par
  `KMP_DUPLICATE_LIB_OK=TRUE` et réordonnancement des imports.
- **Précision du RAG sur requêtes ambiguës** : un modèle 1.5B avec k=3 documents
  généralisait au lieu de citer le mécanisme précis. Résolu en augmentant k=5
  et en contraignant le prompt système à privilégier une cause spécifique du
  contexte plutôt qu'une explication générale.

## Limites connues

- LLM local de 1.5B paramètres : suffisant pour ce périmètre, mais moins
  robuste qu'un modèle plus grand sur des questions hors du corpus fourni.
- Base de connaissances volontairement restreinte (6 documents) pour un MVP —
  une version production nécessiterait un corpus réglementaire plus large
  (validation IVD, procédures internes réelles).
- Dataset de capteurs chimiques utilisé comme proxy pédagogique de dérive
  instrumentale ; pas un dataset de diagnostic clinique réel.