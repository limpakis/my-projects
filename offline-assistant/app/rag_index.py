from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
import os, glob

EMB = OllamaEmbeddings(model="nomic-embed-text")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def load_all(path="docs"):
    docs = []
    for p in glob.glob(f"{path}/**/*", recursive=True):
        if os.path.isdir(p):
            continue
        if p.lower().endswith(".pdf"):
            try:
                docs += PyPDFLoader(p).load()
            except Exception:
                pass
        else:
            try:
                docs += TextLoader(p, encoding="utf-8").load()
            except Exception:
                pass
    return docs


raw_docs = load_all("docs")
if not raw_docs:
    print("No documents found in ./docs — add PDFs or text files first.")
else:
    texts = splitter.split_documents(raw_docs)
    Chroma.from_documents(texts, EMB, collection_name="kb", persist_directory="chroma_db")
    print(f"Indexed {len(texts)} chunks into chroma_db/")


