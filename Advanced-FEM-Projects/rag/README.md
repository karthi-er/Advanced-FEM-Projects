# Local RAG Demo

Chunk plain-text files and retrieve relevant passages with deterministic
lexical term matching. An optional `--answer` step sends the retrieved context
and question to Anthropic. No embeddings are used. Retrieval is a baseline,
not a semantic search system.

## Install and run (Windows PowerShell)

From the portfolio folder:

```powershell
python -m pip install -e .\rag
rag-demo "What should I check in a finite element model?" .\rag\sample_notes.txt
python -m unittest discover -s rag\tests
```

To try the optional answer step, install the extra and provide your own key:

```powershell
python -m pip install -e ".\rag[claude]"
$env:ANTHROPIC_API_KEY = "YOUR_API_KEY"
rag-demo "What should I check?" .\rag\sample_notes.txt --answer
```

The real Anthropic request is **not verified here**; it requires your API key
and network access. Do not commit the key. Errors for missing documents,
invalid chunk/search settings, and missing API credentials are reported clearly.

## Status

This runnable baseline was created because the referenced archive and its
original RAG implementation/results were not supplied. Do not attribute
historical retrieval or answer-quality numbers to this baseline.
