"""
SwiftVisa - RAG Pipeline
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from .env file
load_dotenv()


class RAGPipeline:
    def __init__(self, groq_api_key: str = None, vectorstore_path: str = "vectorstore", top_k: int = 3):
        # Load API key from .env or use provided key
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        # Safety check - ensure API key exists
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found! Please set it in your .env file.")
        
        self.top_k = top_k
        
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        os.environ['TRANSFORMERS_CACHE'] = cache_dir
        
        print("Loading embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print("Loading vector store...")
        self.vectorstore = FAISS.load_local(vectorstore_path, self.embeddings, allow_dangerous_deserialization=True)
        self._llm = None
        print("✅ RAG Pipeline Ready")
    
    @property
    def llm(self):
        if self._llm is None:
            self._llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=self.groq_api_key, temperature=0.1)
        return self._llm
    
    def retrieve(self, query: str, top_k: int = None, country_filter: str = None) -> List[Dict]:
        if top_k is None:
            top_k = self.top_k
        
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k * 2})
        docs = retriever.invoke(query)
        
        if country_filter:
            filtered_docs = [doc for doc in docs if country_filter.lower() in doc.metadata.get('country', '').lower()]
            if len(filtered_docs) >= top_k:
                docs = filtered_docs[:top_k]
            elif filtered_docs:
                docs = filtered_docs + [doc for doc in docs if doc not in filtered_docs][:top_k - len(filtered_docs)]
        
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs[:top_k]]
    
    def query_with_sources(self, query: str, user_profile: dict = None, destination_country: str = None) -> dict:
        retrieved_docs = self.retrieve(query, top_k=self.top_k, country_filter=destination_country)
        
        if not retrieved_docs:
            return {"response": "No policy information found for your destination country.", "status": "NO_RESULTS"}
        
        context = "\n\n".join([f"[{doc['metadata'].get('country', 'Unknown')} - {doc['metadata'].get('visa_type', 'Visa')}]\n{doc['content']}" for doc in retrieved_docs])
        
        prompt = f"""You are a visa eligibility expert for {destination_country or 'the destination country'}.

IMPORTANT RULES:
1. Only assess eligibility based on {destination_country or 'destination country'} visa requirements
2. DO NOT mention or display user profile information (nationality, age, etc.) in your response
3. DO NOT repeat the user's details back to them
4. Only provide visa requirements, eligibility criteria, and next steps
5. Keep response focused on destination country policies only

RETRIEVED {destination_country or 'DESTINATION'} VISA POLICY:
{context}

OUTPUT FORMAT (DO NOT include user profile information):

STATUS: [ELIGIBLE / PARTIALLY ELIGIBLE / NOT ELIGIBLE]

EXPLANATION: [Clear eligibility explanation based on {destination_country or 'destination country'} visa requirements. Do not mention user's nationality, age, or personal details.]

DOCUMENTS: [List specific documents required by {destination_country or 'destination country'}]

NEXT STEPS: [Actionable steps for {destination_country or 'destination country'} visa application]

Remember: Only show visa requirements and eligibility. Do NOT show user profile information."""
        
        try:
            chain = ChatPromptTemplate.from_template(prompt) | self.llm | StrOutputParser()
            response = chain.invoke({})
            
            status = "ELIGIBLE" if "ELIGIBLE" in response.upper() and "NOT" not in response.upper().split("ELIGIBLE")[0] else "PARTIALLY ELIGIBLE" if "PARTIALLY" in response.upper() else "NOT ELIGIBLE"
            
            return {"response": response, "status": status}
            
        except Exception as e:
            return {"response": f"Error: {str(e)}", "status": "ERROR"}


if __name__ == "__main__":
    print("=" * 70)
    print("Testing RAG Pipeline")
    print("=" * 70)
    pipeline = RAGPipeline(top_k=3)
    result = pipeline.query_with_sources("What documents for UK work visa?", destination_country="United Kingdom")
    print(f"\n✅ Status: {result['status']}")
    print(f"\n📄 Response:\n{result['response'][:500]}")
    print("\n" + "=" * 70)