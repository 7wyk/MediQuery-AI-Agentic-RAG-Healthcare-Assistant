from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatQuery, ChatResponse, ChatHistoryResponse
from app.middlewares.auth_middleware import get_current_user
from app.models.user import User
from app.models.analytics import QueryLog
from app.services.vectorstore import get_user_retriever
from app.services.llm import get_llm_chain, query_chain, SimpleRetriever
from app.services.translation import process_multilingual_query, translate_response
from app.services.analytics import log_query, estimate_tokens
import logging
import time

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=ChatResponse)
async def ask_question(
    query: ChatQuery,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Ask a question and get RAG-powered answer from user's documents.
    Supports both Standard RAG and Agentic RAG modes.
    """
    user = await get_current_user(credentials, db)
    start_time = time.time()
    
    try:
        logger.info(f"User {user.id} query: {query.question} (mode={query.mode})")
        
        # ---- Agentic RAG mode ----
        if query.mode == "agentic":
            return await _handle_agentic_rag(query, user, db, start_time)
        
        # ---- Standard RAG mode (existing implementation, unchanged) ----
        # Get relevant documents from user's namespace
        docs = get_user_retriever(user.id, query.question, top_k=3)
        
        if not docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found. Please upload documents first."
            )
        
        # Create retriever and chain
        retriever = SimpleRetriever(documents=docs)
        chain = get_llm_chain(retriever, user_role=user.role)
        
        # Execute query
        result = query_chain(chain, query.question)
        
        # Calculate metrics
        response_time = time.time() - start_time
        token_count = estimate_tokens(query.question + result["answer"])
        
        # Log query for analytics
        log_query(
            db=db,
            user_id=user.id,
            question=query.question,
            answer=result["answer"],
            response_time=response_time,
            token_count=token_count,
            language=query.language
        )
        
        logger.info(f"Query successful in {response_time:.2f}s")
        
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "response_time": response_time,
            "language": query.language,
            "mode": "standard",
            "agent_metadata": None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


async def _handle_agentic_rag(query: ChatQuery, user, db: Session, start_time: float) -> dict:
    """
    Handle Agentic RAG execution with graceful fallback to Standard RAG on failure.
    """
    from app.services.agentic_rag import run_agentic_rag, AgenticRagError

    try:
        result = run_agentic_rag(
            question=query.question,
            user_id=user.id,
            user_role=user.role,
        )

        response_time = time.time() - start_time
        token_count = estimate_tokens(query.question + result["answer"])

        # Log query for analytics
        log_query(
            db=db,
            user_id=user.id,
            question=query.question,
            answer=result["answer"],
            response_time=response_time,
            token_count=token_count,
            language=query.language,
        )

        logger.info(f"Agentic RAG successful in {response_time:.2f}s")

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "response_time": response_time,
            "language": query.language,
            "mode": "agentic",
            "agent_metadata": result.get("agent_metadata"),
        }

    except AgenticRagError as e:
        # Graceful fallback to Standard RAG
        logger.warning(f"Agentic RAG failed, falling back to standard: {e}")

        try:
            docs = get_user_retriever(user.id, query.question, top_k=3)
            if not docs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No documents found. Please upload documents first."
                )

            retriever = SimpleRetriever(documents=docs)
            chain = get_llm_chain(retriever, user_role=user.role)
            result = query_chain(chain, query.question)

            response_time = time.time() - start_time
            token_count = estimate_tokens(query.question + result["answer"])

            log_query(
                db=db,
                user_id=user.id,
                question=query.question,
                answer=result["answer"],
                response_time=response_time,
                token_count=token_count,
                language=query.language,
            )

            return {
                "answer": result["answer"],
                "sources": result["sources"],
                "response_time": response_time,
                "language": query.language,
                "mode": "agentic",
                "agent_metadata": {
                    "retrieval_attempts": 1,
                    "retrieval_refined": False,
                    "documents_retrieved": len(docs),
                    "relevance_score": 0.0,
                    "steps": ["Agentic RAG failed", "Fell back to Standard RAG"],
                    "fallback_to_standard": True,
                },
            }
        except HTTPException:
            raise
        except Exception as fallback_err:
            logger.error(f"Standard RAG fallback also failed: {fallback_err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing question: {str(fallback_err)}"
            )


@router.post("/query-multilang", response_model=ChatResponse)
async def ask_question_multilang(
    query: ChatQuery,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Ask a question in any language - auto-translates to English for RAG, then translates back
    """
    user = await get_current_user(credentials, db)
    start_time = time.time()
    
    try:
        # Detect and translate query to English
        english_question, detected_lang = process_multilingual_query(query.question)
        logger.info(f"Detected language: {detected_lang}, translated: {english_question}")
        
        # Get relevant documents
        docs = get_user_retriever(user.id, english_question, top_k=3)
        
        if not docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found. Please upload documents first."
            )
        
        # Create retriever and chain
        retriever = SimpleRetriever(documents=docs)
        chain = get_llm_chain(retriever, user_role=user.role)
        
        # Execute query in English
        result = query_chain(chain, english_question)
        
        # Translate response back to user's language
        translated_answer = translate_response(result["answer"], detected_lang)
        
        # Calculate metrics
        response_time = time.time() - start_time
        token_count = estimate_tokens(query.question + result["answer"])
        
        # Log query
        log_query(
            db=db,
            user_id=user.id,
            question=query.question,
            answer=translated_answer,
            response_time=response_time,
            token_count=token_count,
            language=detected_lang
        )
        
        return {
            "answer": translated_answer,
            "sources": result["sources"],
            "response_time": response_time,
            "language": detected_lang,
            "mode": "standard",
            "agent_metadata": None,
        }
        
    except Exception as e:
        logger.error(f"Error processing multilingual question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )

@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get chat history for the authenticated user
    """
    user = await get_current_user(credentials, db)
    
    history = db.query(QueryLog).filter(
        QueryLog.user_id == user.id
    ).order_by(QueryLog.timestamp.desc()).limit(limit).all()
    
    return {
        "history": history,
        "total": len(history)
    }

@router.delete("/history")
async def clear_chat_history(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Clear chat history for the authenticated user
    """
    user = await get_current_user(credentials, db)
    
    db.query(QueryLog).filter(QueryLog.user_id == user.id).delete()
    db.commit()
    
    return {"message": "Chat history cleared successfully"}
