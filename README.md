# 🧠 MediQuery AI - Production Full-Stack RAG Application

**MediQuery AI** is a production-ready, full-stack medical document assistant powered by Retrieval-Augmented Generation (RAG) technology. Built with modern React frontend, FastAPI backend, local embeddings, JWT authentication, and comprehensive analytics.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

---

## 🚀 Features

### Core Functionality
- 📄 **Document Management** - Upload, manage, and delete medical PDFs with real-time processing
- 🤖 **AI-Powered Chat** - Ask questions and get accurate, source-cited answers from your documents
- 🔐 **Authentication** - JWT-based auth with role-based access control (Doctor/Student)
- 📊 **Analytics Dashboard** - Track usage, queries, response times, and performance metrics
- 🌍 **Multi-Language Support** - Query in any language with automatic translation
- 🎨 **Modern UI** - Premium SaaS-grade interface with Tailwind CSS and smooth animations

### Technical Features
- **Local Embeddings** - Fast, unlimited document processing using HuggingFace (no API rate limits)
- **RAG Pipeline** - LangChain + Groq LLaMA 3.3 70B + Pinecone vectorstore
- **User Isolation** - Documents stored in user-specific Pinecone namespaces
- **Role-Based Prompting** - Tailored responses for medical professionals vs students
- **Real-time Processing** - Upload progress tracking and status updates
- **Source Citations** - Every answer includes document references with expandable sources
- **Medical Safety** - Built-in constraints to prevent hallucination and inappropriate medical advice

---

## 🧱 Tech Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | FastAPI | High-performance async web framework |
| **Database** | SQLAlchemy (SQLite/PostgreSQL) | ORM for user, document, and analytics data |
| **Authentication** | JWT (python-jose) | Secure token-based authentication |
| **LLM** | Groq API (LLaMA 3.3 70B) | Fast inference for question answering |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) | Local embeddings (384 dimensions) |
| **Vector DB** | Pinecone | Serverless vector database for semantic search |
| **Orchestration** | LangChain | RAG pipeline and retrieval chain |
| **Translation** | deep-translator | Multi-language support |
| **PDF Processing** | PyPDF | Document parsing and text extraction |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | React 18 + TypeScript | Type-safe component-based UI |
| **Build Tool** | Vite | Fast development and optimized builds |
| **Styling** | Tailwind CSS | Utility-first CSS framework |
| **Routing** | React Router v6 | Client-side routing |
| **State** | Context API | Global auth and user state |
| **HTTP Client** | Axios | API communication with interceptors |
| **Charts** | Recharts | Analytics visualizations |
| **Icons** | Lucide React | Modern icon library |

---

## 📁 Project Structure

```
RAG-chatbot/
├── backend/
│   ├── app/
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py          # User model
│   │   │   ├── document.py      # Document model
│   │   │   └── analytics.py     # QueryLog, UsageStats
│   │   ├── routes/              # API endpoints
│   │   │   ├── auth.py          # Authentication routes
│   │   │   ├── documents.py     # Document management
│   │   │   ├── chat.py          # Chat/query endpoints
│   │   │   └── analytics.py     # Analytics endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── auth.py          # JWT, password hashing
│   │   │   ├── vectorstore.py   # Embeddings, Pinecone
│   │   │   ├── llm.py           # LLM chain, prompts
│   │   │   ├── translation.py   # Multi-language
│   │   │   └── analytics.py     # Usage tracking
│   │   ├── middlewares/         # Middleware
│   │   │   └── auth_middleware.py
│   │   ├── schemas/             # Pydantic models
│   │   ├── database.py          # DB configuration
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt         # Python dependencies
│   ├── init_db.py               # Database initialization
│   ├── Procfile                 # Deployment config
│   └── .env.example             # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── pages/               # React pages
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── DocumentsPage.tsx
│   │   │   ├── ChatPage.tsx
│   │   │   └── AnalyticsPage.tsx
│   │   ├── components/          # Reusable components
│   │   │   ├── layout/          # Navbar, Footer
│   │   │   └── common/          # LoadingSpinner, etc.
│   │   ├── services/            # API services
│   │   │   ├── api.ts           # Axios instance
│   │   │   ├── auth.service.ts
│   │   │   ├── document.service.ts
│   │   │   ├── chat.service.ts
│   │   │   └── analytics.service.ts
│   │   ├── contexts/            # React context
│   │   │   └── AuthContext.tsx
│   │   ├── lib/                 # Utilities
│   │   └── main.tsx             # Entry point
│   ├── package.json             # Node dependencies
│   ├── tailwind.config.js       # Tailwind configuration
│   ├── vercel.json              # Vercel deployment
│   └── .env.example             # Environment template
│
├── demo/                        # Sample medical documents
└── README.md                    # This file
```

---

## 🛠️ Local Development Setup

### Prerequisites
- **Python** 3.11+
- **Node.js** 18+
- **npm** or yarn
- **API Keys**:
  - Groq API key (free at [console.groq.com](https://console.groq.com))
  - Pinecone API key (free at [pinecone.io](https://www.pinecone.io/))

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   # Database
   DATABASE_URL=sqlite:///./mediquery.db
   
   # Authentication
   JWT_SECRET=your-secret-key-min-32-characters-long
   JWT_ALGORITHM=HS256
   
   # LLM
   GROQ_API_KEY=your_groq_api_key
   
   # Vector Database
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=medical-local-384
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   
   - API: `http://localhost:8000`
   - Docs: `http://localhost:8000/api/docs`
   - Health: `http://localhost:8000/health`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```
   
   App will be available at `http://localhost:5173`

---

## 🚢 Production Deployment

### Frontend Deployment (Vercel)

1. **Push code to GitHub**

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your repository
   - Set root directory to `frontend`
   - Framework preset: Vite
   
3. **Add environment variable**
   ```
   VITE_API_BASE_URL=https://your-backend-url.com
   ```

4. **Deploy**
   - Vercel auto-deploys on push to main branch

### Backend Deployment (Render)

1. **Create new Web Service**
   - Connect repository
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Add environment variables**
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/mediquery
   JWT_SECRET=your-production-secret-key
   GROQ_API_KEY=your_key
   PINECONE_API_KEY=your_key
   PINECONE_INDEX_NAME=medical-local-384
   ```

3. **Deploy**

---

## 📖 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user profile |

### Document Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/upload` | Upload PDF documents |
| GET | `/api/v1/documents` | List user's documents |
| GET | `/api/v1/documents/{id}/status` | Get document status |
| DELETE | `/api/v1/documents/{id}` | Delete document and vectors |

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/query` | Ask question (English) |
| POST | `/api/v1/chat/query-multilang` | Ask question (any language) |
| GET | `/api/v1/chat/history` | Get chat history |
| DELETE | `/api/v1/chat/history` | Clear chat history |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/overview` | Get usage overview stats |
| GET | `/api/v1/analytics/usage-graph` | Get usage graph data |
| GET | `/api/v1/analytics/top-topics` | Get top queried topics |

---

## 🏗️ Architecture & Data Flow

### RAG Pipeline

```
User Question
    ↓
[1] Embed Query (HuggingFace local model)
    ↓
[2] Search Pinecone (user's namespace)
    ↓
[3] Retrieve Top-K Documents
    ↓
[4] Build Context + Prompt
    ↓
[5] LLM Generation (Groq LLaMA 3.3)
    ↓
[6] Return Answer + Sources
```

### Document Upload Flow

```
PDF Upload
    ↓
[1] Save to disk
    ↓
[2] Create DB record (status: PROCESSING)
    ↓
[3] Load PDF with PyPDF
    ↓
[4] Split into chunks (500 chars, 50 overlap)
    ↓
[5] Generate embeddings (local, batch)
    ↓
[6] Upsert to Pinecone (user namespace)
    ↓
[7] Update DB (status: COMPLETED)
```

### Authentication Flow

```
Login Request
    ↓
[1] Validate credentials
    ↓
[2] Generate JWT tokens (access + refresh)
    ↓
[3] Return tokens to client
    ↓
[4] Client stores in localStorage
    ↓
[5] Axios interceptor adds to requests
    ↓
[6] Backend validates on protected routes
```

---

## 🔒 Security Features

- **JWT Authentication** - Secure token-based auth with expiration
- **Password Hashing** - bcrypt for secure password storage
- **User Isolation** - Documents stored in user-specific Pinecone namespaces
- **CORS Protection** - Configured allowed origins only
- **Input Validation** - Pydantic schemas validate all API inputs
- **SQL Injection Protection** - SQLAlchemy ORM prevents injection
- **Medical Safety** - Prompts explicitly prevent medical advice/diagnosis
- **Rate Limiting** - Can be added with slowapi middleware

---

## 📊 Key Technical Decisions

### Why Local Embeddings?
- **Speed**: 2 seconds vs 2+ minutes with Google API
- **Cost**: Completely free, no API limits
- **Privacy**: Data never leaves your infrastructure
- **Reliability**: No dependency on external API availability

### Why Pinecone?
- **Serverless**: No infrastructure management
- **Fast**: Sub-100ms query latency
- **Scalable**: Handles millions of vectors
- **Namespaces**: Built-in user isolation

### Why Groq?
- **Speed**: Fastest LLM inference (300+ tokens/sec)
- **Free Tier**: Generous free usage
- **Quality**: LLaMA 3.3 70B is highly capable
- **API**: Simple, OpenAI-compatible API

### Why FastAPI?
- **Performance**: Async support, fast execution
- **Type Safety**: Pydantic validation
- **Auto Docs**: Swagger UI out of the box
- **Modern**: Python 3.11+ features

---

## ⚠️ Medical Disclaimer

**IMPORTANT**: MediQuery AI is for **informational and educational purposes only**. It is **NOT a substitute** for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare professionals with any questions regarding medical conditions.

The system is designed with safety constraints:
- Does not provide medical diagnoses
- Does not recommend treatments
- Always cites sources
- Encourages consulting healthcare professionals

---

## 🎯 Performance Metrics

- **Document Upload**: ~2 seconds (6-page PDF)
- **Query Response**: ~3 seconds (including LLM)
- **Embedding Generation**: ~300ms (local)
- **Vector Search**: <100ms (Pinecone)
- **Frontend Build**: ~30 seconds
- **Cold Start**: <5 seconds (serverless)

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] User registration and login
- [ ] Document upload (PDF)
- [ ] Document deletion
- [ ] Chat query with valid documents
- [ ] Chat query without documents (404 error)
- [ ] Multi-language query
- [ ] Analytics dashboard updates
- [ ] Token refresh on expiration
- [ ] Role-based prompt differences

### API Testing

Use the interactive docs at `http://localhost:8000/api/docs` to test all endpoints.

---

## 🤝 Contributing

This is a portfolio project. For questions or suggestions, please open an issue on GitHub.

---

## 📝 License

This project is for educational and portfolio purposes.

---

## � Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

---

## 🚀 Future Enhancements

- [ ] Streaming responses in chat
- [ ] Document OCR support for scanned PDFs
- [ ] Voice input/output
- [ ] Mobile app (React Native)
- [ ] Advanced analytics with ML insights
- [ ] Collaborative features (share documents)
- [ ] Export chat history to PDF
- [ ] Custom model fine-tuning
- [ ] Multi-modal support (images, tables)
- [ ] Real-time collaboration

---

## 📧 Contact

For questions about this project, please open an issue on GitHub.

---

**Built with ❤️ for medical professionals and students**

*Powered by FastAPI, React, LangChain, Groq, and Pinecone*