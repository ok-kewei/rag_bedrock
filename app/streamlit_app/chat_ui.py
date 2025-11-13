# uv run streamlit run app/streamlit_app/chat_ui.py


import streamlit as st
import requests
from langchain_core.messages import AIMessage
import os

# FASTAPI_URL = "http://localhost:8000/rag/query"
FASTAPI_URL = os.getenv("FASTAPI_URL")

st.set_page_config(page_title="Singapore Airlines FAQ RAG Chatbot", layout="centered")
st.title("Singapore Airline FAQ Chatbot")
st.caption(
    """
    Ask questions about Singapore Airlines FAQs. 
    The answers are retrieved from documents stored in ./docs using AWS Bedrock and Claude Sonnet.
    """)

# @st.cache_resource
# def get_rag_chain():
#     try:
#         return load_rag_chain()
#     except Exception as e:
#         st.error(f"Error loading RAG chain: {e}")
#         st.stop()
#
# qa_chain = get_rag_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new input
if prompt := st.chat_input("Ask something about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(FASTAPI_URL, json={"question": prompt})
                print("Response:", response)
                response.raise_for_status()
                data = response.json()
                print("Returns from response.json: ", data)
                answer_text = data.get("answer", "No response")
                # result = qa_chain.invoke({"question": prompt})
                # print("result", result)
                # print("result key",result.keys())

                # answer = result.get("answer") or result.get("result", "")
                # answer = answer.get("answer")
                # sources = result.get("source_documents", [])
                #
                # if sources:
                #     answer += "\n\n**Sources:**\n"
                #     for doc in sources:
                #         source = doc.metadata.get("source", "Unknown")
                #         page = doc.metadata.get("page", "N/A")
                #         answer += f"- {source} (page {page})\n"
                #
                # raw_answer = result.get("answer")
                #
                # if isinstance(raw_answer, AIMessage):
                #     answer_text = raw_answer.content
                # else:
                #     answer_text = str(raw_answer)  # fallback
                #
                # st.markdown(answer_text)
                # st.session_state.messages.append({"role": "assistant", "content": answer_text})
                #
                # print("additional_kwargs",raw_answer.additional_kwargs)
                # print("response metadata",raw_answer.response_metadata)
                # # usage_info = raw_answer.additional_kwargs.get("usage", {}) if isinstance(raw_answer, AIMessage) else {}
                # # print("Token usage info:", usage_info)
                st.markdown(answer_text)
                st.session_state.messages.append({"role": "assistant", "content": answer_text})

                # usage_info = raw_answer.additional_kwargs.get("usage", {}) if isinstance(raw_answer, AIMessage) else {}
                # print("Token usage info:", usage_info)

            except Exception as e:
                st.error(f"An error occurred: {e}")

