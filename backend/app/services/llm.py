from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain.schema import BaseRetriever
from langchain_core.documents import Document
from pydantic import Field
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class SimpleRetriever(BaseRetriever):
    """Simple retriever that returns pre-fetched documents"""
    documents: List[Document] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default_factory=dict)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        return self.documents

def get_llm_chain(retriever: BaseRetriever, user_role: str = "student"):
    """
    Create LLM chain with role-based prompting
    Preserves existing Groq LLaMA3-70B integration
    """
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile"  # Updated to supported model
    )

    # Role-based prompt customization
    role_context = ""
    if user_role == "doctor":
        role_context = "\n- You are assisting a medical professional. Use appropriate medical terminology."
    else:
        role_context = "\n- You are assisting a medical student. Explain concepts clearly and educationally."

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=f"""
You are **MediQuery AI**, an AI-powered assistant trained to help users understand medical documents and health-related questions.

Your job is to provide clear, accurate, and helpful responses based **only on the provided context**.

---

**Context**:
{{context}}

**User Question**:
{{question}}

---

**Answer**:
- Respond in a calm, factual, and respectful tone.
- Use simple explanations when needed.{role_context}
- If the context does not contain the answer, say: "I'm sorry, but I couldn't find relevant information in the provided documents."
- Do NOT make up facts.
- Do NOT give medical advice or diagnoses.
- Always cite the source document when providing information.
"""
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

def query_chain(chain, question: str) -> dict:
    """
    Execute query and return formatted result
    """
    result = chain.invoke({"query": question})  # Updated from deprecated __call__
    
    return {
        "answer": result["result"],
        "sources": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in result.get("source_documents", [])
        ]
    }
