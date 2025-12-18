#!/usr/bin/env bash
set -e

echo "🚀 Bootstrapping NLP Semantic Search + RAG project..."

# Root folders
mkdir -p app data/{raw,processed,index} scripts tests

# App modules
touch app/__init__.py
touch app/{api.py,rag.py,retriever.py,ingest.py,chunking.py,cleaning.py,embeddings.py,store_faiss.py,store_chroma.py,schemas.py,settings.py}

# Scripts
touch scripts/{ingest_folder.py,build_index.py}

# Tests
touch tests/__init__.py

# Config & meta
touch requirements.txt
touch README.md
touch .env.example
touch Makefile

echo "✅ Directory structure created"

cat <<EOF

Next steps:
1) Fill requirements.txt
2) Paste Makefile content
3) Run:
   make dev

Structure:
.
├── app/
├── data/
│   ├── raw/
│   ├── processed/
│   └── index/
├── scripts/
├── tests/
├── Makefile
├── requirements.txt
└── README.md

EOF
