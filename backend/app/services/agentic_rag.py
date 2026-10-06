"""
Agentic RAG implementation using LangGraph.

Implements a stateful workflow:
  Query Analysis → Retrieval → Relevance Grading → (Rewrite if needed) → Answer Generation

Reuses existing Pinecone vectorstore and Groq LLM infrastructure.
"""

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.documents import Document as LCDocument
from app.services.vectorstore import get_user_retriever
import os
import logging
import json

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MAX_RETRIEVAL_ATTEMPTS = 2


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    """Typed state flowing through the LangGraph workflow."""
    original_question: str
    current_question: str
    user_id: int
    user_role: str
    documents: List[LCDocument]
    context: str
    answer: str
    sources: List[Dict[str, Any]]
    retrieval_attempts: int
    retrieval_refined: bool
    relevance_score: float
    mode: str
    steps: List[str]  # high-level execution events for the frontend


# ---------------------------------------------------------------------------
# Shared LLM helper
# ---------------------------------------------------------------------------

def _get_groq_llm() -> ChatGroq:
    """Return the shared Groq LLM instance used across all nodes."""
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="openai/gpt-oss-120b",
        temperature=0,
    )


# ---------------------------------------------------------------------------
# Node 1 — Query Analyzer
# ---------------------------------------------------------------------------

def analyze_query(state: AgentState) -> AgentState:
    """
    Lightweight query normalization.
    Strips conversational filler and produces a clean retrieval query.
    Does NOT answer the question or perform diagnosis.
    """
    llm = _get_groq_llm()
    prompt = (
        "You are a query optimizer for a medical document retrieval system.\n"
        "Given the user's question, produce a concise, normalized search query "
        "that will maximize retrieval relevance from medical documents.\n"
        "Do NOT answer the question. Do NOT provide medical advice.\n"
        "Only output the optimized search query, nothing else.\n\n"
        f"User question: {state['original_question']}\n\n"
        "Optimized search query:"
    )

    try:
        response = llm.invoke(prompt)
        current_question = response.content.strip()
        # Fallback if the LLM returns empty or garbage
        if not current_question or len(current_question) < 5:
            current_question = state["original_question"]
    except Exception as e:
        logger.warning(f"Query analysis failed, using original: {e}")
        current_question = state["original_question"]

    state["current_question"] = current_question
    state["steps"].append("Query analyzed")
    logger.info(f"Analyzed query: '{state['original_question']}' → '{current_question}'")
    return state


# ---------------------------------------------------------------------------
# Node 2 — Retrieve Documents
# ---------------------------------------------------------------------------

def retrieve_documents(state: AgentState) -> AgentState:
    """
    Retrieve documents from Pinecone using the EXISTING get_user_retriever.
    Always scoped to user_{user_id} namespace.
    """
    state["retrieval_attempts"] += 1

    try:
        docs = get_user_retriever(
            user_id=state["user_id"],
            question=state["current_question"],
            top_k=5,
        )
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        docs = []

    state["documents"] = docs

    # Build context string and source list from retrieved documents
    context_parts = []
    sources = []
    for doc in docs:
        context_parts.append(doc.page_content)
        sources.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
        })

    state["context"] = "\n\n".join(context_parts)
    state["sources"] = sources

    step_msg = f"Retrieved {len(docs)} documents (attempt {state['retrieval_attempts']})"
    state["steps"].append(step_msg)
    logger.info(step_msg)
    return state


# ---------------------------------------------------------------------------
# Node 3 — Relevance Grader
# ---------------------------------------------------------------------------

def grade_documents(state: AgentState) -> AgentState:
    """
    Evaluate whether retrieved documents are relevant enough to answer the question.
    Uses Groq LLM for lightweight grading. Does NOT generate the final answer.
    """
    if not state["documents"]:
        state["relevance_score"] = 0.0
        state["steps"].append("No documents to grade")
        return state

    llm = _get_groq_llm()
    prompt = (
        "You are a relevance grader for a medical document retrieval system.\n"
        "Given a user question and retrieved document context, determine if the "
        "context contains enough relevant information to answer the question.\n\n"
        "Respond ONLY with a JSON object in this exact format:\n"
        '{"relevant": true, "score": 0.85}\n\n'
        "- 'relevant' is a boolean (true if documents are sufficient, false otherwise)\n"
        "- 'score' is a float between 0.0 and 1.0 indicating relevance confidence\n\n"
        "Do NOT explain your reasoning. Do NOT answer the question.\n\n"
        f"Question: {state['current_question']}\n\n"
        f"Context:\n{state['context'][:3000]}\n\n"
        "JSON response:"
    )

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        # Parse JSON from the response — handle markdown code blocks
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        result = json.loads(content)
        state["relevance_score"] = float(result.get("score", 0.5))
        is_relevant = result.get("relevant", True)
    except Exception as e:
        logger.warning(f"Relevance grading parse failed, defaulting to relevant: {e}")
        state["relevance_score"] = 0.6
        is_relevant = True

    status = "sufficient" if is_relevant else "insufficient"
    state["steps"].append(f"Context relevance: {status} (score: {state['relevance_score']:.2f})")
    logger.info(f"Relevance grade: {status}, score={state['relevance_score']}")
    return state


# ---------------------------------------------------------------------------
# Node 4 — Query Rewriter
# ---------------------------------------------------------------------------

def rewrite_query(state: AgentState) -> AgentState:
    """
    Rewrite the query to improve retrieval when documents were graded as insufficient.
    Does NOT answer the question.
    """
    llm = _get_groq_llm()
    prompt = (
        "You are a query rewriter for a medical document retrieval system.\n"
        "The previous retrieval did not return sufficiently relevant results.\n"
        "Rewrite the query to improve retrieval from medical documents.\n"
        "Make the query more specific and use medical terminology where appropriate.\n"
        "Do NOT answer the question. Only output the improved search query.\n\n"
        f"Original question: {state['original_question']}\n"
        f"Previous search query: {state['current_question']}\n\n"
        "Improved search query:"
    )

    try:
        response = llm.invoke(prompt)
        new_query = response.content.strip()
        if not new_query or len(new_query) < 5:
            new_query = state["original_question"]
    except Exception as e:
        logger.warning(f"Query rewrite failed, using original: {e}")
        new_query = state["original_question"]

    state["current_question"] = new_query
    state["retrieval_refined"] = True
    state["steps"].append(f"Query refined")
    logger.info(f"Rewritten query: '{new_query}'")
    return state


# ---------------------------------------------------------------------------
# Node 5 — Generate Answer
# ---------------------------------------------------------------------------

def generate_answer(state: AgentState) -> AgentState:
    """
    Generate the final answer using the existing medical safety constraints.
    Reuses the same prompt structure from llm.py.
    """
    # Role-based prompt customization (matches existing llm.py behavior)
    if state["user_role"] == "doctor":
        role_context = "\n- You are assisting a medical professional. Use appropriate medical terminology."
    else:
        role_context = "\n- You are assisting a medical student. Explain concepts clearly and educationally."

    # Handle empty context
    if not state["context"].strip():
        state["answer"] = (
            "I'm sorry, but I couldn't find relevant information in your uploaded documents "
            "to answer this question. Please ensure you've uploaded documents that contain "
            "information related to your query."
        )
        state["steps"].append("Answer generated (insufficient context)")
        return state

    llm = _get_groq_llm()
    prompt = (
        "You are **MediQuery AI**, an AI-powered assistant trained to help users "
        "understand medical documents and health-related questions.\n\n"
        "Your job is to provide clear, accurate, and helpful responses based "
        "**only on the provided context**.\n\n"
        "---\n\n"
        f"**Context**:\n{state['context']}\n\n"
        f"**User Question**:\n{state['original_question']}\n\n"
        "---\n\n"
        "**Answer**:\n"
        "- Respond in a calm, factual, and respectful tone.\n"
        f"- Use simple explanations when needed.{role_context}\n"
        '- If the context does not contain the answer, say: "I\'m sorry, but I '
        'couldn\'t find relevant information in the provided documents."\n'
        "- Do NOT make up facts.\n"
        "- Do NOT give medical advice or diagnoses.\n"
        "- Always cite the source document when providing information.\n"
    )

    try:
        response = llm.invoke(prompt)
        state["answer"] = response.content.strip()
    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        state["answer"] = (
            "I encountered an error while generating the answer. "
            "Please try again or switch to Standard RAG mode."
        )

    state["steps"].append("Final answer generated")
    return state


# ---------------------------------------------------------------------------
# Conditional routing
# ---------------------------------------------------------------------------

def should_rewrite_or_generate(state: AgentState) -> str:
    """
    Conditional edge after grade_documents.
    Routes to rewrite_query if relevance is low AND retries remain,
    otherwise routes to generate_answer.
    """
    is_relevant = state["relevance_score"] >= 0.6
    can_retry = state["retrieval_attempts"] < MAX_RETRIEVAL_ATTEMPTS

    if not is_relevant and can_retry:
        logger.info("Routing to rewrite_query (insufficient relevance, retries available)")
        return "rewrite_query"
    else:
        if not is_relevant:
            logger.info("Routing to generate_answer (insufficient relevance but max retries reached)")
        else:
            logger.info("Routing to generate_answer (sufficient relevance)")
        return "generate_answer"


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------

def build_agentic_graph() -> StateGraph:
    """
    Build the LangGraph StateGraph for Agentic RAG.

    Flow:
      analyze_query → retrieve_documents → grade_documents
        → (relevant) → generate_answer → END
        → (not relevant & retries left) → rewrite_query → retrieve_documents → ...
        → (not relevant & max retries) → generate_answer → END
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("retrieve_documents", retrieve_documents)
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("rewrite_query", rewrite_query)
    workflow.add_node("generate_answer", generate_answer)

    # Set entry point
    workflow.set_entry_point("analyze_query")

    # Add edges
    workflow.add_edge("analyze_query", "retrieve_documents")
    workflow.add_edge("retrieve_documents", "grade_documents")

    # Conditional routing after grading
    workflow.add_conditional_edges(
        "grade_documents",
        should_rewrite_or_generate,
        {
            "rewrite_query": "rewrite_query",
            "generate_answer": "generate_answer",
        },
    )

    # After rewriting, retrieve again
    workflow.add_edge("rewrite_query", "retrieve_documents")

    # After generating, finish
    workflow.add_edge("generate_answer", END)

    return workflow.compile()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

# Compile the graph once at module level for reuse
_agentic_graph = None


def _get_graph():
    """Lazy-initialize the compiled graph."""
    global _agentic_graph
    if _agentic_graph is None:
        _agentic_graph = build_agentic_graph()
    return _agentic_graph


def run_agentic_rag(
    question: str,
    user_id: int,
    user_role: str = "student",
) -> Dict[str, Any]:
    """
    Execute the Agentic RAG workflow.

    Returns a dict compatible with the existing ChatResponse schema:
      {
        "answer": str,
        "sources": [...],
        "mode": "agentic",
        "agent_metadata": { ... }
      }
    """
    initial_state: AgentState = {
        "original_question": question,
        "current_question": question,
        "user_id": user_id,
        "user_role": user_role,
        "documents": [],
        "context": "",
        "answer": "",
        "sources": [],
        "retrieval_attempts": 0,
        "retrieval_refined": False,
        "relevance_score": 0.0,
        "mode": "agentic",
        "steps": [],
    }

    try:
        graph = _get_graph()
        final_state = graph.invoke(initial_state)

        return {
            "answer": final_state["answer"],
            "sources": final_state["sources"],
            "mode": "agentic",
            "agent_metadata": {
                "retrieval_attempts": final_state["retrieval_attempts"],
                "retrieval_refined": final_state["retrieval_refined"],
                "documents_retrieved": len(final_state["documents"]),
                "relevance_score": round(final_state["relevance_score"], 2),
                "steps": final_state["steps"],
                "fallback_to_standard": False,
            },
        }
    except Exception as e:
        logger.error(f"Agentic RAG failed, falling back to standard: {e}")
        # Graceful fallback — return metadata indicating the fallback
        raise AgenticRagError(str(e))


class AgenticRagError(Exception):
    """Raised when the agentic RAG pipeline fails unrecoverably."""
    pass
