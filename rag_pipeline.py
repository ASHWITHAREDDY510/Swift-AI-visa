"""
SwiftVisa - RAG Pipeline (Deployment Safe Version)
"""

import os
from typing import List, Dict

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class RAGPipeline:
    def __init__(self, groq_api_key: str = None, vectorstore_path: str = "vectorstore", top_k: int = 3):

        # ✅ FIX 1: Support Streamlit Secrets + Local
        try:
            import streamlit as st
            self.groq_api_key = groq_api_key or st.secrets.get("GROQ_API_KEY")
        except:
            self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

        # ❗ Safety check
        if not self.groq_api_key:
            raise ValueError("❌ GROQ_API_KEY not found! Add it in Streamlit Secrets.")

        self.top_k = top_k

        # Cache directory for embeddings
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        os.environ['TRANSFORMERS_CACHE'] = cache_dir

        print("🔄 Loading embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # ✅ FIX 2: Safe vectorstore loading
        if os.path.exists(vectorstore_path):
            print("📦 Loading vector store...")
            self.vectorstore = FAISS.load_local(
                vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            print("⚠️ Vectorstore not found → Running without RAG")
            self.vectorstore = None

        self._llm = None
        print("✅ RAG Pipeline Ready")

    @property
    def llm(self):
        if self._llm is None:
            self._llm = ChatGroq(
                model="llama-3.1-8b-instant",
                groq_api_key=self.groq_api_key,
                temperature=0.1
            )
        return self._llm

    # ---------------- RETRIEVE ----------------
    def retrieve(self, query: str, top_k: int = None, country_filter: str = None) -> List[Dict]:

        # ✅ FIX 3: If no vectorstore → skip retrieval
        if self.vectorstore is None:
            return []

        if top_k is None:
            top_k = self.top_k

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})
        docs = retriever.invoke(query)

        return [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in docs
        ]

    # ---------------- MAIN QUERY ----------------
    def query_with_sources(self, query: str, user_profile: dict = None, destination_country: str = None) -> dict:

        retrieved_docs = self.retrieve(query)

        # If no RAG → fallback
        if retrieved_docs:
            context = "\n\n".join([doc["content"] for doc in retrieved_docs])
        else:
            context = "No policy documents available. Provide general visa guidance."

        prompt = f"""
You are a visa eligibility expert.

User Question:
{query}

Context:
{context}

Provide:

1. STATUS: (ELIGIBLE / PARTIALLY ELIGIBLE / NOT ELIGIBLE)
2. Explanation
3. Required Documents
4. Next Steps
"""

        try:
            chain = ChatPromptTemplate.from_template(prompt) | self.llm | StrOutputParser()
            response = chain.invoke({})

            # Basic status detection
            response_upper = response.upper()

            if "NOT ELIGIBLE" in response_upper:
                status = "NOT ELIGIBLE"
            elif "PARTIALLY" in response_upper:
                status = "PARTIALLY ELIGIBLE"
            elif "ELIGIBLE" in response_upper:
                status = "ELIGIBLE"
            else:
                status = "UNKNOWN"

            return {
                "response": response,
                "status": status
            }

        except Exception as e:
            return {
                "response": f"❌ Error: {str(e)}",
                "status": "ERROR"
            }


# ---------------- TEST ----------------
if __name__ == "__main__":
    print("=" * 60)
    print("Testing RAG Pipeline")
    print("=" * 60)

    pipeline = RAGPipeline(top_k=3)

    result = pipeline.query_with_sources(
        "What documents are needed for UK work visa?",
        destination_country="United Kingdom"
    )

    print(f"\nStatus: {result['status']}")
    print(f"\nResponse:\n{result['response'][:500]}")