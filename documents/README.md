# Documents

Place `.txt` documents in this directory before running the document-ingestion script.

These files are split into overlapping chunks, converted into embeddings, and stored locally in ChromaDB.

Example:

```text
documents/
├── document_1.txt
├── document_2.txt
└── document_3.txt
```

Files matching `documents/*.txt` are excluded from version control by `.gitignore`.