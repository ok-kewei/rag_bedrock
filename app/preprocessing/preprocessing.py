import os
from langchain_aws.llms import BedrockLLM
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_aws.chat_models import ChatBedrock
from langchain_core.runnables import RunnableLambda


# --- Configuration ---
AWS_REGION = "us-east-1"
LLM_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
CHROMA_DIR = "../chroma_db"  # Make sure this directory exists for your vector DB

def load_rag_chain():
    """
    Loads and returns the RAG chain using the LCEL pipe approach.
    """

    # 1️Initialize components
    llm = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        region_name="us-east-1",
        temperature=0.1,
        max_tokens=512
    )
    embeddings = BedrockEmbeddings(model_id=EMBEDDING_MODEL_ID, region_name=AWS_REGION)
    # vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

    # Setting this os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is None, because
    # On Lambda, it skips initializing Chroma — avoiding file permission and timeout issues.
    # locally (where AWS_LAMBDA_FUNCTION_NAME is not defined), it will still create/load Chroma.

    # Choose path based on environment
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is None:
        # local development
        persist_dir = "./chroma_db"
    else:
        # inside Lambda, you can use /tmp or a mounted EFS/S3 path
        persist_dir = "/tmp/chroma_db"  # or wherever your DB is available

    vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = vectorstore.as_retriever()

    # 2️Define prompt template
    prompt = PromptTemplate(
        template="Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:",
        input_variables=["context", "question"]
    )

    # 3 Use rag chain using LCEL pipe-style approach
    def retriever_to_text(query: str) -> str:
        # Retrieve documents relevant to the query
        docs = retriever.get_relevant_documents(query)
        return "\n\n".join([d.page_content for d in docs])

    # rag_chain = (
    #     retriever_to_text
    #     | (lambda context, query: {"context": context, "question": query})  # Add context and question
    #     | prompt
    #     | llm  # Use the LLM to generate the response
    #     | StrOutputParser()  # Convert the output to string
    # )

    # The argument you pass to .invoke(), in this case, {"question": prompt}. x = {"question": prompt}
    # RunnableLambda(lambda x: x["question"]) means take the dictionary input, and return the value stored under the key question.
    # So if x = {"question": "What is AWS Bedrock?"},     # then this step outputs "What is AWS Bedrock?".
    # retriever input is "What is AWS Bedrock?" , output a list of Document objects,[Document(...), Document(...)]
    # runnableLambda concatenate context (text),
    # prompt takes input of {context, question}, outputs formatted prompt string
    # llm takes the prompt string generated answer text

    # "question": RunnableLambda(lambda x: x["question"])
    # Input: {"question": "What is AWS Bedrock?"}, Output: "What is AWS Bedrock?"

    rag_chain = (
            {
                # "context": retriever | RunnableLambda(lambda docs: "\n\n".join([d.page_content for d in docs])),
                "context": RunnableLambda(lambda x: x["question"]) | retriever | RunnableLambda(
                    lambda docs: "\n\n".join([d.page_content for d in docs])),
                # "question": RunnableLambda(lambda x: x["query"])
                "question": RunnableLambda(lambda x: x["question"])
            }
            | prompt
            | llm
            # | StrOutputParser()
            | RunnableLambda(lambda output: {"answer": output})
    )

    return rag_chain
