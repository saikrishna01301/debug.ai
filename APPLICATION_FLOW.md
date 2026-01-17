# DebugAI Application Flow Documentation

## Complete User Journey: Error Input → LLM Response

This document explains the complete flow of how DebugAI processes user errors, from the moment they paste an error log to receiving AI-generated solutions.

---

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [Complete User Flow](#complete-user-flow)
3. [Stage-by-Stage Data Transformation](#stage-by-stage-data-transformation)
4. [Database Schema](#database-schema)
5. [Key Components & Functions](#key-components--functions)

---

## High-Level Architecture

```mermaid
graph TB
    User[👤 User] -->|Pastes Error Log| Frontend[🎨 Next.js Frontend]
    Frontend -->|HTTP POST /api/analyze| Backend[⚙️ FastAPI Backend]
    Backend -->|1. Parse| Parser[📝 ErrorParser]
    Backend -->|2. Search| VectorDB[(🔍 ChromaDB<br/>Vector Store)]
    Backend -->|3. Analyze| LLM[🤖 GPT-4o<br/>GitHub Models]
    Backend -->|4. Store| Database[(💾 Supabase<br/>PostgreSQL)]
    Backend -->|Response| Frontend
    Frontend -->|Display Solutions| User

    style Frontend fill:#61dafb
    style Backend fill:#009688
    style Parser fill:#ff9800
    style VectorDB fill:#9c27b0
    style LLM fill:#4caf50
    style Database fill:#2196f3
```

---

## Complete User Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant FE as 🎨 Frontend (Next.js)
    participant BE as ⚙️ Backend (FastAPI)
    participant P as 📝 ErrorParser
    participant V as 🔍 VectorStore
    participant L as 🤖 LLM (GPT-4o)
    participant DB as 💾 Database (Supabase)

    U->>FE: Paste error log & click "Analyze"
    Note over FE: frontend/app/page.tsx<br/>handleAnalyze()

    FE->>BE: POST /api/analyze<br/>{query: "error log", limit: 5}
    Note over BE: backend/app/main.py<br/>analyze_error()

    BE->>P: parser.parse(request.query)
    Note over P: services/parser.py<br/>parse()
    P-->>BE: parsed_error dict

    BE->>V: vc.search(search_query, n_results=5)
    Note over V: services/vector_store.py<br/>search()
    V-->>BE: search_results<br/>(documents, metadata, distances)

    BE->>DB: create_parsed_error(session, parsed_error)
    Note over DB: db/crud/error_crud.py<br/>create_parsed_error()
    DB-->>BE: db_error (with id)

    BE->>L: llm.analyze_error(parsed_error, search_results)
    Note over L: services/llm_analyzer.py<br/>analyze_error()
    L-->>BE: analysis_result<br/>(root_cause, reasoning, solutions)

    BE->>DB: create_analysis(session, analysis_data)
    Note over DB: db/crud/error_crud.py<br/>create_analysis()
    DB-->>BE: db_analysis (with id)

    BE-->>FE: AnalysisResponse JSON
    FE-->>U: Display solutions with code examples
```

---

## Stage-by-Stage Data Transformation

### Stage 0: User Input (Frontend)

**Location:** `frontend/app/page.tsx:20`
**Function:** `handleAnalyze()`

```javascript
// User input
const errorLog = `
Traceback (most recent call last):
  File "app.py", line 3, in <module>
    from flask import Flask
ImportError: No module named 'flask'
`
```

**API Call:**
```javascript
apiService.analyze(errorLog, 5)
// POST http://localhost:8000/api/analyze
// Body: { "query": "Traceback...", "limit": 5 }
```

---

### Stage 1: Error Parsing

**Location:** `backend/app/main.py:53`
**Function:** `parser.parse(request.query)`
**Implementation:** `backend/app/services/parser.py`

**Input:**
```python
request.query = """
Traceback (most recent call last):
  File "app.py", line 3, in <module>
    from flask import Flask
ImportError: No module named 'flask'
"""
```

**Output (parsed_error dict):**
```python
{
    "error_type": "ImportError",
    "error_message": "No module named 'flask'",
    "language": "python",
    "framework": None,
    "file_path": "app.py",
    "line_number": 3,
    "function_name": "<module>",
    "stack_trace": [
        {
            "file": "app.py",
            "line": 3,
            "function": "<module>",
            "code": "from flask import Flask"
        }
    ],
    "confidence_score": 95
}
```

**Key Functions:**
- `ErrorParser.parse()` - Main parsing entry point
- `_parse_python_error()` - Python-specific parsing
- `_extract_stack_trace()` - Extract stack frames

---

### Stage 2: Vector Search (RAG)

**Location:** `backend/app/main.py:61`
**Function:** `vc.search(search_query, n_results=5)`
**Implementation:** `backend/app/services/vector_store.py`

**Search Query Construction:**
```python
# From main.py:56-59
if parsed_error and parsed_error.get("error_type") and parsed_error.get("error_message"):
    search_query = f"{parsed_error['error_type']}: {parsed_error['error_message']}"
else:
    search_query = request.query

# Result: "ImportError: No module named 'flask'"
```

**Vector Search Process:**
```mermaid
graph LR
    A[Search Query:<br/>ImportError: No module named 'flask'] -->|Embed| B[Query Vector<br/>1536 dimensions]
    B -->|Compare| C[ChromaDB<br/>100 Stack Overflow posts]
    C -->|Cosine Similarity| D[Top 5 Results<br/>Sorted by distance]

    style A fill:#fff3cd
    style B fill:#d1ecf1
    style C fill:#d4edda
    style D fill:#f8d7da
```

**Output (search_results):**
```python
{
    "documents": [
        [
            "Title:ImportError: No module named flask Question:I'm getting ImportError when trying to import Flask... Answer:You need to install Flask using pip install flask...",
            "Title:Python module not found Question:Getting module not found error... Answer:...",
            "Title:How to install Flask Question:... Answer:...",
            "Title:ImportError solutions Question:... Answer:...",
            "Title:Python dependencies Question:... Answer:..."
        ]
    ],
    "metadatas": [
        [
            {"title": "ImportError: No module named flask", "url": "https://stackoverflow.com/q/12345", "tags": "python, flask", "votes": 234},
            {"title": "Python module not found", "url": "https://stackoverflow.com/q/67890", "tags": "python, import", "votes": 156},
            ...
        ]
    ],
    "distances": [
        [0.12, 0.23, 0.34, 0.45, 0.56]  # Lower = more similar
    ]
}
```

**Formatted for LLM (search_results_dicts):**
```python
[
    {
        "content": "Title:ImportError: No module named flask Question:I'm getting ImportError...",
        "title": "ImportError: No module named flask",
        "url": "https://stackoverflow.com/q/12345",
        "tags": ["python", "flask"],
        "votes": 234,
        "distance": 0.12
    },
    {
        "content": "Title:Python module not found Question:Getting module not found...",
        "title": "Python module not found",
        "url": "https://stackoverflow.com/q/67890",
        "tags": ["python", "import"],
        "votes": 156,
        "distance": 0.23
    },
    ...
]
```

**Key Functions:**
- `VectorStore.search()` - Main search entry point
- `VectorStore._embed_query()` - Convert query to vector
- `collection.query()` - ChromaDB similarity search

---

### Stage 3: Database Storage (Parsed Error)

**Location:** `backend/app/main.py:96-99`
**Function:** `create_parsed_error(session, parsed_error)`
**Implementation:** `backend/app/db/crud/error_crud.py`

**Input Preparation:**
```python
# Add raw error log for storage
parsed_error["raw_error_log"] = request.query
```

**Database Insert:**
```python
# error_crud.py:5-25
async def create_parsed_error(session: AsyncSession, parsed_error_data: dict) -> ParsedError:
    error_data = {
        "raw_error_log": parsed_error_data.get("raw_error_log", ""),
        "error_type": parsed_error_data.get("error_type", ""),
        "error_message": parsed_error_data.get("error_message", ""),
        "language": parsed_error_data.get("language"),
        "framework": parsed_error_data.get("framework"),
        "file_name": parsed_error_data.get("file_path"),
        "line_number": parsed_error_data.get("line_number"),
        "function_name": parsed_error_data.get("function_name"),
        "stack_trace": parsed_error_data.get("stack_trace"),
        "confidence_score": parsed_error_data.get("confidence_score"),
    }

    parsed_error = ParsedError(**error_data)
    session.add(parsed_error)
    await session.commit()
    await session.refresh(parsed_error)
    return parsed_error
```

**Database Record (Supabase - parsed_errors table):**
```sql
INSERT INTO parsed_errors (
    raw_error_log, error_type, error_message, language,
    file_name, line_number, function_name, stack_trace,
    confidence_score, created_at
) VALUES (
    'Traceback (most recent call last):\n  File "app.py"...',
    'ImportError',
    'No module named ''flask''',
    'python',
    'app.py',
    3,
    '<module>',
    '[{"file": "app.py", "line": 3, ...}]'::jsonb,
    95,
    NOW()
);

-- Returns: id = 42
```

**Output:**
```python
db_error = ParsedError(
    id=42,
    raw_error_log="Traceback...",
    error_type="ImportError",
    error_message="No module named 'flask'",
    language="python",
    file_name="app.py",
    line_number=3,
    function_name="<module>",
    stack_trace=[...],
    confidence_score=95,
    created_at=datetime(2024, 1, 13, 10, 30, 0)
)
```

---

### Stage 4: LLM Analysis

**Location:** `backend/app/main.py:101`
**Function:** `llm.analyze_error(parsed_error, search_results_dicts)`
**Implementation:** `backend/app/services/llm_analyzer.py`

**LLM Context Building:**
```python
# llm_analyzer.py:90-109
def _build_context(self, search_results):
    context_parts = []
    for i, result in enumerate(search_results):
        content = result.get("content")[:800]
        context_parts.append(f"""
--- Source {i} (Votes: {result.get('votes', 0)}, Relevance: {1 - result['distance']:.2f}) ---
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Tags: {', '.join(result.get('tags', []))}
Content:{content}
        """)
    return "\n".join(context_parts)
```

**LLM Prompt:**
```python
# System Prompt (llm_analyzer.py:47-62)
system_prompt = """You are an expert debugging assistant helping developers solve errors.
Your job:
1. Analyze the error with provided context from Stack Overflow and documentation
2. Identify the root cause with step-by-step reasoning
3. Provide 2-3 ranked solutions with code examples
4. Include confidence scores for each solution
5. Link to relevant sources

Guidelines:
- Prioritize solutions from highly-voted Stack Overflow posts
- Consider the user's language/framework
- Explain WHY each solution works, not just HOW
- Be honest about uncertainty (confidence < 0.7 if unsure)
- Keep solutions practical and actionable
"""

# User Prompt (llm_analyzer.py:64-82)
user_prompt = f"""Please analyze this error:

ERROR DETAILS:
- Type: ImportError
- Message: No module named 'flask'
- Language: python
- File: app.py
- Line: 3
- Function: <module>

RAW ERROR LOG:
Traceback (most recent call last):
  File "app.py", line 3, in <module>
    from flask import Flask
ImportError: No module named 'flask'

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
--- Source 0 (Votes: 234, Relevance: 0.88) ---
Title: ImportError: No module named flask
URL: https://stackoverflow.com/q/12345
Tags: python, flask
Content: Title:ImportError: No module named flask Question:I'm getting ImportError when trying to import Flask... Answer:You need to install Flask using pip install flask...

--- Source 1 (Votes: 156, Relevance: 0.77) ---
...

Provide your analysis with root cause, reasoning, and solutions.
"""
```

**LLM API Call (Structured Output):**
```python
# llm_analyzer.py:30-38
response = self.client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    tools=[self._get_analysis_function()],
    tool_choice={"type": "function", "function": {"name": "provide_analysis"}},
)
```

**Function Schema for Structured Output:**
```python
# llm_analyzer.py:113-174
{
    "type": "function",
    "function": {
        "name": "provide_analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "root_cause": {"type": "string"},
                "reasoning": {"type": "string"},
                "solutions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "explanation": {"type": "string"},
                            "code": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "source_urls": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "minItems": 2,
                    "maxItems": 3
                }
            }
        }
    }
}
```

**LLM Output (analysis_result):**
```python
{
    "root_cause": "The Flask module is not installed in the Python environment",

    "reasoning": "The ImportError occurs when Python cannot find the 'flask' module in its installed packages. This typically happens because:\n1. Flask was never installed\n2. It's installed in a different Python environment\n3. The virtual environment is not activated",

    "solutions": [
        {
            "title": "Install Flask using pip",
            "explanation": "The most common solution is to install Flask using pip. This will download and install Flask and its dependencies in your current Python environment.",
            "code": "pip install flask\n# Or if you're using Python 3 specifically:\npip3 install flask",
            "confidence": 0.95,
            "source_urls": [
                "https://stackoverflow.com/q/12345",
                "https://flask.palletsprojects.com/installation/"
            ]
        },
        {
            "title": "Activate your virtual environment",
            "explanation": "If you're using a virtual environment, make sure it's activated before running your script. Flask might be installed in the venv but not accessible if the environment isn't active.",
            "code": "# On Linux/Mac:\nsource venv/bin/activate\n\n# On Windows:\nvenv\\Scripts\\activate\n\n# Then run your script:\npython app.py",
            "confidence": 0.85,
            "source_urls": ["https://stackoverflow.com/q/67890"]
        },
        {
            "title": "Install in requirements.txt",
            "explanation": "For production or team projects, add Flask to requirements.txt to ensure consistent dependencies across environments.",
            "code": "# Create/update requirements.txt:\necho 'flask==2.3.0' >> requirements.txt\n\n# Install all requirements:\npip install -r requirements.txt",
            "confidence": 0.80,
            "source_urls": ["https://stackoverflow.com/q/54321"]
        }
    ]
}
```

**Key Functions:**
- `LLMAnalyzer.analyze_error()` - Main analysis entry point
- `_build_context()` - Format RAG results for LLM
- `_get_system_prompt()` - System instructions
- `_create_user_prompt()` - Error details + context
- `_get_analysis_function()` - Structured output schema

---

### Stage 5: Database Storage (Analysis)

**Location:** `backend/app/main.py:104-111`
**Function:** `create_analysis(session, analysis_data)`
**Implementation:** `backend/app/db/crud/error_crud.py`

**Input Preparation:**
```python
analysis_data = {
    "parsed_error_id": db_error.id,  # 42 (foreign key)
    "root_cause": llm_response.get("root_cause", ""),
    "reasoning": llm_response.get("reasoning", ""),
    "solutions": llm_response.get("solutions", []),  # JSON array
    "sources_used": len(search_results),  # 5
}
```

**Database Insert:**
```python
# error_crud.py:28-36
async def create_analysis(session: AsyncSession, analysis_data: dict) -> Analysis:
    analysis = Analysis(**analysis_data)
    session.add(analysis)
    await session.commit()
    await session.refresh(analysis)
    return analysis
```

**Database Record (Supabase - analyses table):**
```sql
INSERT INTO analyses (
    parsed_error_id, root_cause, reasoning, solutions,
    sources_used, created_at
) VALUES (
    42,  -- Foreign key to parsed_errors
    'The Flask module is not installed in the Python environment',
    'The ImportError occurs when Python cannot find...',
    '[
        {
            "title": "Install Flask using pip",
            "explanation": "The most common solution...",
            "code": "pip install flask\n# Or if you''re using...",
            "confidence": 0.95,
            "source_urls": ["https://stackoverflow.com/q/12345", ...]
        },
        ...
    ]'::jsonb,
    5,
    NOW()
);

-- Returns: id = 123
```

**Database Relationship:**
```mermaid
erDiagram
    PARSED_ERRORS ||--o{ ANALYSES : "has many"

    PARSED_ERRORS {
        int id PK
        text raw_error_log
        string error_type
        string error_message
        string language
        string file_name
        int line_number
        jsonb stack_trace
        timestamp created_at
    }

    ANALYSES {
        int id PK
        int parsed_error_id FK
        text root_cause
        text reasoning
        jsonb solutions
        int sources_used
        timestamp created_at
    }
```

**Output:**
```python
db_analysis = Analysis(
    id=123,
    parsed_error_id=42,
    root_cause="The Flask module is not installed...",
    reasoning="The ImportError occurs when...",
    solutions=[
        {
            "title": "Install Flask using pip",
            "explanation": "The most common solution...",
            "code": "pip install flask...",
            "confidence": 0.95,
            "source_urls": [...]
        },
        ...
    ],
    sources_used=5,
    created_at=datetime(2024, 1, 13, 10, 30, 5)
)
```

---

### Stage 6: API Response

**Location:** `backend/app/main.py:114-125`
**Schema:** `backend/app/schemas/analysis.py`

**Response Construction:**
```python
analysis_result = AnalysisResponse(
    error_type=parsed_error.get("error_type"),           # "ImportError"
    error_message=parsed_error.get("error_message"),     # "No module named 'flask'"
    language=parsed_error.get("language", "unknown"),    # "python"
    file_path=parsed_error.get("file_path"),             # "app.py"
    line_number=parsed_error.get("line_number"),         # 3
    root_cause=llm_response.get("root_cause", ""),       # From LLM
    reasoning=llm_response.get("reasoning", ""),         # From LLM
    solutions=llm_response.get("solutions", []),         # From LLM
    sources_used=len(search_results),                    # 5
    analysis_id=db_analysis.id                           # 123
)

return analysis_result
```

**JSON Response Sent to Frontend:**
```json
{
    "error_type": "ImportError",
    "error_message": "No module named 'flask'",
    "language": "python",
    "file_path": "app.py",
    "line_number": 3,
    "root_cause": "The Flask module is not installed in the Python environment",
    "reasoning": "The ImportError occurs when Python cannot find the 'flask' module...",
    "solutions": [
        {
            "title": "Install Flask using pip",
            "explanation": "The most common solution is to install Flask using pip...",
            "code": "pip install flask\n# Or if you're using Python 3 specifically:\npip3 install flask",
            "confidence": 0.95,
            "source_urls": [
                "https://stackoverflow.com/q/12345",
                "https://flask.palletsprojects.com/installation/"
            ]
        },
        {
            "title": "Activate your virtual environment",
            "explanation": "If you're using a virtual environment...",
            "code": "# On Linux/Mac:\nsource venv/bin/activate\n...",
            "confidence": 0.85,
            "source_urls": ["https://stackoverflow.com/q/67890"]
        },
        {
            "title": "Install in requirements.txt",
            "explanation": "For production or team projects...",
            "code": "# Create/update requirements.txt:\necho 'flask==2.3.0' >> requirements.txt\n...",
            "confidence": 0.80,
            "source_urls": ["https://stackoverflow.com/q/54321"]
        }
    ],
    "sources_used": 5,
    "analysis_id": 123
}
```

---

### Stage 7: Frontend Display

**Location:** `frontend/app/page.tsx:20-22`
**Components:** `frontend/components/ResultsSection.tsx`

**State Update:**
```javascript
const data = await apiService.analyze(errorLog, 5);
setResult(data);  // Triggers re-render
```

**Rendered UI:**
```jsx
{result && <ResultsSection result={result} />}
```

**Display to User:**
- ✅ Error type and message highlighted
- 📝 Root cause explanation
- 💡 Step-by-step reasoning
- 🔧 3 ranked solutions with:
  - Solution title
  - Detailed explanation
  - Code examples with syntax highlighting
  - Confidence score (95%, 85%, 80%)
  - Stack Overflow source links
- 📊 Metadata: 5 sources used, analysis ID #123

---

## Database Schema

### parsed_errors Table
```sql
CREATE TABLE parsed_errors (
    id SERIAL PRIMARY KEY,
    raw_error_log TEXT NOT NULL,
    error_type VARCHAR(255) NOT NULL,
    error_message VARCHAR(255) NOT NULL,
    language VARCHAR(50),
    framework VARCHAR(50),
    file_name VARCHAR(255),
    line_number INTEGER,
    function_name VARCHAR(255),
    stack_trace JSONB,
    confidence_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### analyses Table
```sql
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    parsed_error_id INTEGER NOT NULL REFERENCES parsed_errors(id),
    root_cause TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    solutions JSONB NOT NULL,  -- Array of solution objects
    sources_used INTEGER,
    analysis_time INTEGER,  -- milliseconds
    created_at TIMESTAMP DEFAULT NOW()
);
```

### stackoverflow_posts Table (Knowledge Base)
```sql
CREATE TABLE stackoverflow_posts (
    id SERIAL PRIMARY KEY,
    question_id INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    question_body TEXT NOT NULL,
    answer_body TEXT NOT NULL,
    tags TEXT[] NOT NULL,
    votes INTEGER NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT NOW()
);
```

---

## Key Components & Functions

### Frontend (Next.js + TypeScript)

| File | Key Functions | Purpose |
|------|---------------|---------|
| `frontend/app/page.tsx` | `handleAnalyze()` | Main user interaction handler |
| `frontend/services/api.ts` | `apiService.analyze()` | HTTP client for backend API |
| `frontend/components/InputSection.tsx` | - | Error log textarea input |
| `frontend/components/ResultsSection.tsx` | - | Display analysis results |

### Backend (FastAPI + Python)

| File | Key Functions | Purpose |
|------|---------------|---------|
| `backend/app/main.py` | `analyze_error()` | Main API endpoint orchestrator |
| `backend/app/services/parser.py` | `ErrorParser.parse()`<br/>`_parse_python_error()`<br/>`_extract_stack_trace()` | Parse error logs into structured data |
| `backend/app/services/vector_store.py` | `VectorStore.search()`<br/>`_embed_query()`<br/>`add_documents()` | ChromaDB vector search operations |
| `backend/app/services/llm_analyzer.py` | `LLMAnalyzer.analyze_error()`<br/>`_build_context()`<br/>`_create_user_prompt()`<br/>`_get_analysis_function()` | LLM-powered error analysis |
| `backend/app/db/crud/error_crud.py` | `create_parsed_error()`<br/>`create_analysis()` | Database operations for errors & analyses |
| `backend/app/db/session.py` | `get_session()`<br/>`init_db()` | Database session management |

### Data Models

| File | Models | Purpose |
|------|--------|---------|
| `backend/app/db/models/error.py` | `ParsedError`<br/>`Analysis` | SQLAlchemy ORM models |
| `backend/app/schemas/analysis.py` | `AnalysisResponse`<br/>`Solution` | Pydantic response schemas |
| `frontend/services/api.ts` | `AnalysisResult`<br/>`Solution` | TypeScript interfaces |

---

## Data Flow Diagram

```mermaid
graph TD
    A[User Pastes Error Log] -->|1. HTTP POST| B[Backend: analyze_error]

    B -->|2. Parse| C[ErrorParser]
    C -->|parsed_error dict| D{Valid Parse?}
    D -->|No| E[Create Minimal Dict]
    D -->|Yes| F[Add raw_error_log]
    E --> F

    F -->|3. Search| G[VectorStore.search]
    G -->|Embed Query| H[GitHub Models API]
    H -->|Query Vector| I[ChromaDB]
    I -->|Top 5 Results| J[Format Results]

    F -->|4. Store Error| K[create_parsed_error]
    K -->|Insert| L[(Supabase DB)]
    L -->|db_error with id| M[Build Analysis Request]

    J --> M
    M -->|5. Analyze| N[LLMAnalyzer]
    N -->|Build Context| O[Format RAG Results]
    O -->|Create Prompts| P[GPT-4o API Call]
    P -->|Structured Output| Q[Parse LLM Response]

    Q -->|6. Store Analysis| R[create_analysis]
    R -->|Insert with FK| L
    L -->|db_analysis with id| S[Build Response]

    Q --> S
    J --> S
    K --> S

    S -->|7. Return JSON| T[Frontend]
    T -->|8. Display| U[User Sees Solutions]

    style A fill:#fff3cd
    style U fill:#d4edda
    style L fill:#cfe2ff
    style P fill:#f8d7da
```

---

## RAG (Retrieval-Augmented Generation) Flow

```mermaid
graph LR
    subgraph "Knowledge Base Preparation (One-time)"
        A1[Stack Overflow Posts] -->|Scrape| A2[Supabase DB]
        A2 -->|Fetch| A3[create_embeddings.py]
        A3 -->|Embed| A4[GitHub Models API]
        A4 -->|Vectors| A5[(ChromaDB)]
    end

    subgraph "Runtime Query (Per Request)"
        B1[User Error Query] -->|Embed| B2[GitHub Models API]
        B2 -->|Query Vector| B3[Search ChromaDB]
        A5 -.->|Similarity Search| B3
        B3 -->|Top K Results| B4[RAG Context]
        B4 -->|Augment| B5[LLM Prompt]
        B5 -->|Generate| B6[GPT-4o]
        B6 -->|Solutions| B7[User]
    end

    style A5 fill:#e7f3ff
    style B3 fill:#fff3cd
    style B6 fill:#d4edda
```

---

## Error Handling Scenarios

### Scenario 1: Error Found in RAG
- Vector search returns relevant Stack Overflow posts (distance < 0.3)
- LLM gets rich context from community solutions
- High confidence solutions (0.8-0.95)
- Source URLs included

### Scenario 2: Error NOT Found in RAG
- Vector search returns poor matches (distance > 0.8) or empty results
- LLM falls back to general knowledge
- Lower confidence solutions (0.5-0.7)
- Generic or no source URLs
- System still provides helpful analysis

### Scenario 3: Parser Fails
- Create minimal `parsed_error` dict with "Unknown" type
- Continue with raw error log
- LLM can still extract information from raw text

---

## Environment Variables Required

```bash
# Backend (.env)
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx  # For embeddings & LLM
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Performance Metrics

| Stage | Typical Duration | Notes |
|-------|------------------|-------|
| Parse Error | 10-50ms | Regex-based, very fast |
| Vector Search | 50-200ms | Depends on collection size |
| DB Insert (Error) | 20-100ms | Async operation |
| LLM Analysis | 2-5 seconds | Main bottleneck |
| DB Insert (Analysis) | 20-100ms | Async operation |
| **Total** | **2.5-6 seconds** | End-to-end |

---

## Tech Stack Summary

**Frontend:**
- Next.js 14 (React)
- TypeScript
- Tailwind CSS
- Axios (HTTP client)

**Backend:**
- FastAPI (Python)
- SQLAlchemy (ORM)
- Pydantic (Validation)
- OpenAI SDK (LLM & Embeddings)

**Databases:**
- Supabase (PostgreSQL) - Structured data
- ChromaDB - Vector embeddings

**AI Services:**
- GitHub Models (Azure OpenAI)
  - GPT-4o for analysis
  - text-embedding-3-small for vectors

---

## Future Enhancements

1. **Cache frequently asked errors** - Reduce LLM costs
2. **User feedback loop** - Improve solutions over time
3. **Multi-language support** - Expand beyond Python
4. **Real-time updates** - WebSocket for streaming responses
5. **Analytics dashboard** - Track common errors
6. **Browser extension** - Capture errors directly from IDE

---

**Last Updated:** 2024-01-14
**Version:** 1.0
**Author:** [Your Name]
