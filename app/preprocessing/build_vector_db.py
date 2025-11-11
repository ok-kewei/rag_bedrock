# preprocessing/build_vector_db.py

import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_aws import BedrockEmbeddings

AWS_REGION = "us-east-1"
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
PDF_DIRECTORY = "../../docs"
CHROMA_DB_DIR = "../../chroma_db"


def build_vector_db():
    print("Building vector database...")
    # 1️Load PDF documents
    if not os.path.exists(PDF_DIRECTORY):
        raise FileNotFoundError(f"PDF directory not found: {PDF_DIRECTORY}")

    loader = PyPDFDirectoryLoader(PDF_DIRECTORY)
    documents = loader.load()
    if not documents:
        raise ValueError("No PDF files found in the directory. Please add PDFs to ./docs")
    print(f"Loaded {len(documents)} document pages.")

    # 2️Splits into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # 3️Create Embeddings
    embeddings = BedrockEmbeddings(model_id=EMBEDDING_MODEL_ID, region_name=AWS_REGION)

    # 4️Create Vector Database
    if not os.path.exists(CHROMA_DB_DIR):
        os.makedirs(CHROMA_DB_DIR)

    vectorstore = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    # vectorstore.persist()
    print(f"Vector store saved at {CHROMA_DB_DIR}")


if __name__ == "__main__":
    build_vector_db()
    print("Vector database build complete!")
