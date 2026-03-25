rag_pipeline.py

"""
SwiftVisa - Milestone 2: RAG Retrieval Pipeline
Core retrieval logic for visa policy search
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


class RAGPipeline:
    """RAG Pipeline for SwiftVisa eligibility screening"""
    
    def __init__(self, 
                 vectorstore_path="vectorstore",
                 embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                 llm_model="llama3.2:1b",
                 top_k=3):
        """
        Initialize RAG pipeline
        
        Args:
            vectorstore_path: Path to FAISS vector store
            embedding_model: SentenceTransformer model for embeddings
            llm_model: Ollama model name for LLM
            top_k: Number of chunks to retrieve
        """
        self.vectorstore_path = vectorstore_path
        self.top_k = top_k
        self.llm_model = llm_model
        
        # Load embeddings
        print("Loading embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load vector store
        print("Loading vector store...")
        self.vectorstore = FAISS.load_local(
            vectorstore_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        print("RAG Pipeline initialized")
        self._llm = None
    
    @property
    def llm(self):
        """Lazy load LLM"""
        if self._llm is None:
            print(f"Loading LLM: {self.llm_model}...")
            try:
                self._llm = Ollama(model=self.llm_model, temperature=0.1)
                print("LLM loaded")
            except Exception as e:
                print(f"LLM not available: {e}")
                self._llm = None
        return self._llm
    
    def _extract_metadata_from_content(self, content: str) -> Dict[str, str]:
        """Extract country and visa_type from chunk content header"""
        result = {"country": "Unknown", "visa_type": "Unknown", "source_file": "Unknown"}
        
        lines = content.split('\n')[:10]
        
        # Pattern 1: ## Country - VisaType Visa
        for line in lines:
            line = line.strip()
            if line.startswith('## ') and '-' in line:
                parts = line.replace('##', '').strip().split('-')
                if len(parts) >= 2:
                    result["country"] = parts[0].strip()
                    visa = parts[1].replace('Visa', '').strip()
                    result["visa_type"] = visa if visa else "Unknown"
                    break
        
        # Pattern 2: ### Source: filename.txt
        for line in lines:
            if line.startswith('### Source:'):
                result["source_file"] = line.replace('### Source:', '').strip()
                break
        
        return result
    
    def retrieve(self, query: str, filters=None) -> List[Dict]:
        """
        Retrieve top-K relevant policy chunks
        
        Args:
            query: User query
            filters: Optional metadata filters
        
        Returns:
            List of retrieved documents with metadata
        """
        # Get retriever
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.top_k, "filter": filters}
        )
        
        # Retrieve documents
        docs = retriever.invoke(query)
        
        # Format results with enriched metadata
        results = []
        for i, doc in enumerate(docs, 1):
            meta = doc.metadata
            
            # Get metadata from vector store
            country = meta.get('country') or meta.get('Country')
            visa_type = meta.get('visa_type') or meta.get('VisaType')
            source = meta.get('source_file') or meta.get('source')
            
            # Fallback: extract from content
            if not country or country == 'Unknown':
                extracted = self._extract_metadata_from_content(doc.page_content)
                if extracted["country"] != "Unknown":
                    country = extracted["country"]
                if extracted["visa_type"] != "Unknown":
                    visa_type = extracted["visa_type"]
                if extracted["source_file"] != "Unknown":
                    source = extracted["source_file"]
            
            results.append({
                "rank": i,
                "content": doc.page_content,
                "metadata": {
                    "country": country or "Unknown",
                    "visa_type": visa_type or "Unknown",
                    "source_file": source or "Unknown",
                    "chunk_id": meta.get('chunk_id', i)
                },
                "relevance_score": meta.get('score', 'N/A')
            })
        
        return results
    
    def format_context(self, documents: List[Dict]) -> str:
        """Format retrieved documents into context string for LLM"""
        formatted = []
        for doc in documents:
            meta = doc['metadata']
            country = meta.get('country', 'Unknown')
            visa_type = meta.get('visa_type', 'Unknown')
            source = meta.get('source_file', 'Unknown')
            formatted.append(
                f"[Source: {country} - {visa_type} Visa]\n"
                f"[File: {source}]\n"
                f"{doc['content']}\n---"
            )
        return "\n\n".join(formatted)
    
    def generate_response(self, query: str, user_profile: Dict) -> Dict:
        """Generate complete RAG response"""
        # Step 1: Retrieve
        retrieved_docs = self.retrieve(query)
        
        if not retrieved_docs:
            return {
                "query": query,
                "response": "No relevant policy information found.",
                "retrieved_documents": [],
                "confidence": "Low",
                "status": "NO_RESULTS"
            }
        
        # Step 2: Format context
        context = self.format_context(retrieved_docs)
        
        # Step 3: Generate with LLM (or retrieval-only if LLM unavailable)
        if self.llm is None:
            return {
                "query": query,
                "response": "LLM not available. Retrieved:\n\n" + context,
                "retrieved_documents": retrieved_docs,
                "confidence": "Medium",
                "status": "RETRIEVAL_ONLY"
            }
        
        # Step 4: Build prompt
        template = """You are SwiftVisa, an expert immigration assistant.

RETRIEVED POLICY INFORMATION:
{context}

USER PROFILE:
- Nationality: {nationality}
- Destination: {destination_country}
- Visa Type: {visa_type}
- Purpose: {purpose}

OUTPUT FORMAT:
## Eligibility Assessment
**Status:** [ELIGIBLE / PARTIALLY ELIGIBLE / NOT ELIGIBLE]
**Confidence:** [High / Medium / Low]
**Requirements Met:** [List]
**Required Documents:** [List]
**Next Steps:** [List]
**Sources:** [Cite policy sources]
"""
        prompt = ChatPromptTemplate.from_template(template)
        
        # Step 5: Build chain
        chain = prompt | self.llm | StrOutputParser()
        
        # Step 6: Generate response
        try:
            response = chain.invoke({
                "context": context,
                "nationality": user_profile.get('nationality', 'N/A'),
                "destination_country": user_profile.get('destination_country', 'N/A'),
                "visa_type": user_profile.get('visa_type', 'N/A'),
                "purpose": user_profile.get('purpose', 'N/A')
            })
            
            # Parse confidence and status
            confidence = "High" if "Confidence:** High" in response else "Medium"
            status = "ELIGIBLE" if "**Status:** ELIGIBLE" in response else "PARTIALLY ELIGIBLE"
            
            return {
                "query": query,
                "response": response,
                "retrieved_documents": retrieved_docs,
                "confidence": confidence,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "query": query,
                "response": f"Error: {str(e)}",
                "retrieved_documents": retrieved_docs,
                "confidence": "Low",
                "status": "ERROR"
            }


def test_pipeline():
    """Test the RAG pipeline"""
    print("Testing RAG Pipeline")
    print("=" * 60)
    pipeline = RAGPipeline(top_k=3)
    
    test_query = "What documents for UK work visa?"
    profile = {
        "nationality": "Indian",
        "destination_country": "United Kingdom",
        "visa_type": "Work Visa",
        "purpose": "Employment"
    }
    
    result = pipeline.generate_response(test_query, profile)
    print(f"Status: {result['status']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Response: {result['response'][:300]}...")


if __name__ == "__main__":
    test_pipeline()