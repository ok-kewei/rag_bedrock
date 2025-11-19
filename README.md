# RAG FastAPI Chatbot (Docker + AWS Lambda Deployment)

## Overview
Traditional FAQ pages often require users to manually search through information, leading to frustration and inefficiency. This is a Retrieval-Augmented Generation (RAG) chatbot application built with FastAPI.

It answers user questions based on a set of documents stored in the `./docs` folder.  
In this example, I used Singapore Airlines’ FAQ. Therefore, it addresses the traditional, rigid way of FAQ by enabling users to ask natural-language questions and receive precise, context-grounded answers directly from Singapore Airlines’ FAQ documents.

The system combines:

* **FastAPI** for serving API requests
* **LLM model** for answer generation
* **Vector database + embeddings** for retrieval
* **Docker** for local development and deployment
* **AWS Lambda + ECR** for serverless production hosting

This makes the chatbot fast, cost-efficient, and easy to deploy.

---

## What This Project Does
- Loads your Singapore Airlines FAQ or any documents from `./docs`
- Converts them into embeddings
- Stores them in a vector store
- Accepts questions via an API (`/rag`)
- Retrieves the most relevant chunks
- Uses the LLM to generate an accurate answer
- Runs locally with Docker or deploys to AWS Lambda

---
## Architecture Diagram
             ┌─────────────────────┐
             │     User / UI       │
             └──────────┬──────────┘
                        │ HTTP POST /rag
                        ▼
               ┌───────────────────┐
               │     FastAPI       │
               │  (Mangum Adapter) │
               └──────────┬────────┘
                          │ Calls RAG pipeline
                          ▼
            ┌────────────────────────┐
            │      Retriever          │
            │ (Embeddings + VectorDB) │
            └──────────┬─────────────┘
                       │ Top-k chunks
                       ▼
             ┌──────────────────────┐
             │        LLM           │
             └──────────┬───────────┘
                        │ Final Answer
                        ▼
             ┌──────────────────────┐
             │       FastAPI         │
             └──────────────────────┘


## Quick Start — Clone, Virtualenv, Install, Setup `.env`

These are the local setup steps you asked for. Use these before running or building the Docker image (recommended for development).

1. **Clone the repo**

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

2. **Create & activate a Python virtual environment**

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Windows (cmd):

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

3. **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If you use `requirements-dev.txt` for development dependencies, install it too:

```bash
pip install -r requirements-dev.txt
```

4. **Copy / create `.env`**

If the repo contains `.env.example`:

```bash
cp .env.example .env
```

Open `.env` and update these (example keys):

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT="rag-demo"
FASTAPI_URL=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
```

Notes:

* Do **not** add quotes around values unless the value itself contains spaces and you want them to be literal.
* Keep `.env` out of version control; `.gitignore` should contain `.env`.

5. **If you want to initialize vectorstore / index documents**

To build your own vector database (vectorstore) using the documents in the ./docs directory, run the indexing script now.:

```bash
python app/preprocessing/build_vector_db.py
```

This script:

- loads everything inside ./docs/
- splits into chunks
- embeds each chunk
- inserts the embeddings into the vectorstore ( CHROMA_DB_DIR = "../../chroma_db")

You run this script only once, or whenever your documents change.


This process is called indexing where we
1. Convert your documents into embeddings
(e.g., Singapore Airlines FAQ PDFs, text files, etc.)

2. Store those embeddings in a vector database
(e.g., Chroma, FAISS, SQLite-based vector store, etc.)

---

## Local Development (Docker)

### 1️Build Image

```bash
docker build -t rag-fastapi .
```

### 2️Run Locally (preferred for matching production)

```
docker run --env-file .env -p 8000:8000 rag-fastapi
```

### 3️Test the API

```
curl -XPOST "http://localhost:8000/rag" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is your baggage policy?"}'
```

Or open interactive docs:

```
http://localhost:8000/docs
```

---

## Deployment to AWS Lambda (Container Image)

### 1️ Tag & Push to ECR

```bash
aws ecr get-login-password --region ap-southeast-1 | docker login \
    --username AWS --password-stdin <your-aws-account>.dkr.ecr.ap-southeast-1.amazonaws.com

docker build -t rag-fastapi .
docker tag rag-fastapi:latest <ecr-url>:latest
docker push <ecr-url>:latest
```

### 2️ Deploy Lambda

* In the AWS Console create a new Lambda, choose **Container image** and select your image from ECR.
* Configure memory, timeout and environment variables in the Lambda Console.
* Optionally create a Lambda Function URL (for public HTTP access) or put it behind API Gateway for auth, throttling and usage plans.

---

## Example Request & Response

### Request

```
POST /rag
{
  "question": "Does Singapore Airlines allow cabin pets?"
}
```

### Response

```json
{
  "answer": "Based on your documents: Singapore Airlines does not allow pets in the cabin, except for assistance dogs."
}
```
---

## Langsmith
Monitoring & Tracing with LangSmith

This project includes built‑in LangSmith tracing to help track and debug your RAG pipeline.

### How It Works

LangSmith is automatically enabled when you set the following in your .env:
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=rag_demo
```

### Where Tracing Happens

Tracing is integrated inside app/api/rag_router.py, where the RAG chain is invoked:

result = rag_chain.invoke({"question": request.question})

Every call to rag_chain.invoke() automatically generates a LangSmith trace.

### What We Will See in LangSmith

- Full RAG pipeline breakdown (retriever → LLM → output)
- Input question & generated answer
- Token usage
- Latency per component
- Any errors or exceptions

Metadata such as model used, prompt templates, retriever hits

### Viewing Your Traces

Visit LangSmith project: https://smith.langchain.com/

<img width="1596" height="952" alt="Screenshot from 2025-11-19 22-08-49" src="https://github.com/user-attachments/assets/b5c47772-3e89-4c2c-b63c-9ab0ddde44b9" />



---

## Future Improvements


1. Add API Key Authentication. This is to prevent unauthorized access and avoids unexpected costs from misuse of your API.
2. Use an external vector database (e.g., Chroma or Aurora on EC2) instead of storing locally
   Ensures persistence, scalability, and faster retrieval. Lambda containers are ephemeral, so local storage is not reliable in production.
3. Replace Streamlit with a production-ready front-end (Next.js).
   Streamlit is suitable for internal demos or prototypes, but not ideal for a production front-end due to limited UI flexibility, server-side rendering only, and scaling challenges.
   Next.js (or similar frameworks) allows better UI customization, supports streaming responses, and scales well with multiple users.

---



