from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handlers import catch_exception_middleware
from routes.upload_pdfs import router as upload_router
from routes.ask_question import router as ask_router
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(title="Medical Assistant API",
              description="API for AI Medical Assistant Chatbot")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


app.middleware("http")(catch_exception_middleware)


app.include_router(upload_router)

app.include_router(ask_router)
