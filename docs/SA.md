# 🦞 Lobster K8s Copilot - System Architecture (SA)

> **Version**: 1.0 | **Date**: 2026-03-07 | **Status**: Approved

---

## 1. System Context Diagram

```mermaid
C4Context
    title System Context - Lobster K8s Copilot

    Person(user, "DevOps Engineer", "Validates YAML, diagnoses pods")
    
    System(lobster, "Lobster K8s Copilot", "AI-powered K8s YAML management & diagnostics")
    
    System_Ext(k8s, "Kubernetes Cluster", "Target cluster for monitoring")
    System_Ext(ollama, "Ollama", "Local LLM server")
    System_Ext(openai, "OpenAI API", "Cloud LLM provider")
    System_Ext(gemini, "Google Gemini API", "Cloud LLM provider")
    
    Rel(user, lobster, "Uses", "HTTPS")
    Rel(lobster, k8s, "Reads pod status, logs, events", "K8s API")
    Rel(lobster, ollama, "AI requests (local-first)", "HTTP")
    Rel(lobster, openai, "AI requests (fallback)", "HTTPS")
    Rel(lobster, gemini, "AI requests (fallback)", "HTTPS")
```

---

## 2. Container Diagram

```mermaid
C4Container
    title Container Diagram - Lobster K8s Copilot

    Person(user, "User")
    
    Container(frontend, "Frontend", "React + Tailwind CSS", "Dashboard UI with Monaco Editor")
    Container(backend, "Backend API", "Python FastAPI", "REST API with rate limiting, auth")
    Container(ai_engine, "AI Engine", "Python", "Multi-model LLM router")
    ContainerDb(db, "Database", "SQLite/PostgreSQL", "Stores diagnosis history")
    
    System_Ext(k8s, "Kubernetes API")
    System_Ext(llm, "LLM Providers")
    
    Rel(user, frontend, "Uses", "HTTPS")
    Rel(frontend, backend, "API calls", "REST/JSON")
    Rel(backend, ai_engine, "Diagnosis requests", "HTTP")
    Rel(backend, db, "Persist history", "SQL")
    Rel(backend, k8s, "Pod info, logs", "K8s SDK")
    Rel(ai_engine, llm, "LLM inference", "HTTPS")
```

---

## 3. Component Architecture

### 3.1 Backend Components

```mermaid
graph TB
    subgraph "Backend (FastAPI)"
        MAIN[main.py<br/>App Entry + Middleware]
        
        subgraph "API Layer"
            V1[v1/router.py]
            PC[pod_controller]
            DC[diagnose_controller]
            YC[yaml_controller]
        end
        
        subgraph "Service Layer"
            PS[PodService]
            DS[DiagnoseService]
            YS[YamlService]
        end
        
        subgraph "Repository Layer"
            DR[DiagnoseRepository]
        end
        
        subgraph "Middleware"
            RL[Rate Limiter]
            CORS[CORS]
            AUTH[API Key Auth]
            SEC[Security Headers]
        end
        
        DB[(SQLite/PostgreSQL)]
    end
    
    MAIN --> V1
    MAIN --> RL
    MAIN --> CORS
    MAIN --> AUTH
    MAIN --> SEC
    
    V1 --> PC
    V1 --> DC
    V1 --> YC
    
    PC --> PS
    DC --> DS
    YC --> YS
    
    DS --> DR
    DR --> DB
```

### 3.2 AI Engine Components

```mermaid
graph TB
    subgraph "AI Engine"
        DIAG[AIDiagnoser<br/>Multi-model Router]
        
        subgraph "Analyzers"
            OA[OllamaAnalyzer<br/>Local-first]
            OAIA[OpenAIAnalyzer<br/>Cloud fallback]
            GA[GeminiAnalyzer<br/>Cloud fallback]
        end
        
        BASE[BaseAnalyzer<br/>Abstract Interface]
        PROMPTS[k8s_prompts.py<br/>Prompt Templates]
    end
    
    DIAG --> OA
    DIAG --> OAIA
    DIAG --> GA
    
    OA -.-> BASE
    OAIA -.-> BASE
    GA -.-> BASE
    
    DIAG --> PROMPTS
```

---

## 4. Data Flow

### 4.1 YAML Scan Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend
    participant YS as YamlService
    
    U->>FE: Paste YAML in editor
    U->>FE: Click "Scan"
    FE->>BE: POST /api/v1/yaml/scan
    BE->>YS: scan(yaml_content)
    YS->>YS: Parse YAML
    YS->>YS: Run anti-pattern rules
    YS-->>BE: YamlScanResponse
    BE-->>FE: JSON response
    FE-->>U: Display issues
```

### 4.2 AI Diagnosis Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend
    participant DS as DiagnoseService
    participant K8S as Kubernetes API
    participant AI as AI Engine
    participant LLM as LLM Provider
    
    U->>FE: Select pod, click "Diagnose"
    FE->>BE: POST /api/v1/diagnose/{pod_name}
    BE->>DS: diagnose(pod_name, namespace)
    DS->>K8S: get_pod(), get_logs(), get_events()
    K8S-->>DS: Pod details
    DS->>DS: Mask sensitive data
    DS->>AI: diagnose(context)
    AI->>AI: Select provider (local-first)
    AI->>LLM: Send prompt
    LLM-->>AI: JSON response
    AI-->>DS: DiagnoseResult
    DS->>DS: Save to history
    DS-->>BE: DiagnoseResponse
    BE-->>FE: JSON response
    FE-->>U: Display diagnosis
```

---

## 5. Deployment Architecture

### 5.1 Docker Compose (Development)

```mermaid
graph LR
    subgraph "Docker Compose"
        FE[frontend:3000]
        BE[backend:8000]
        AI[ai_engine:8001]
        DB[(SQLite file)]
    end
    
    USER[Browser] --> FE
    FE --> BE
    BE --> AI
    BE --> DB
```

### 5.2 Kubernetes (Production)

```mermaid
graph TB
    subgraph "K8s Namespace: lobster"
        ING[Ingress<br/>TLS termination]
        
        subgraph "Deployments"
            FE[Frontend Pod<br/>Nginx + React]
            BE[Backend Pod<br/>FastAPI]
            AI[AI Engine Pod]
        end
        
        SVC_FE[Service: frontend]
        SVC_BE[Service: backend]
        SVC_AI[Service: ai-engine]
        
        CM[ConfigMap]
        SEC[Secret<br/>API keys]
        PVC[PVC<br/>SQLite data]
    end
    
    ING --> SVC_FE
    ING --> SVC_BE
    SVC_FE --> FE
    SVC_BE --> BE
    BE --> SVC_AI
    SVC_AI --> AI
    BE --> PVC
    BE --> CM
    BE --> SEC
    AI --> SEC
```

---

## 6. Security Architecture

### 6.1 Authentication & Authorization

| Layer | Mechanism |
|-------|-----------|
| API | Optional API key via `X-API-Key` or `Bearer` token |
| K8s | ServiceAccount with RBAC (read-only pods, logs, events) |
| Database | Application-level access only |

### 6.2 Data Security

| Concern | Mitigation |
|---------|------------|
| Secrets in logs | Regex-based masking before sending to LLM |
| CORS | Configurable allowed origins |
| Headers | X-Frame-Options, X-Content-Type-Options, HSTS |
| Input validation | Pydantic schemas with size limits |

---

## 7. Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Backend | Python + FastAPI | 3.11+ / 0.100+ |
| Frontend | React + Tailwind | 18+ / 3+ |
| AI Engine | Python + httpx | 3.11+ |
| Database | SQLAlchemy + SQLite/PostgreSQL | 2.0+ |
| Container | Docker + docker-compose | 24+ / 2+ |
| Orchestration | Kubernetes | 1.25+ |

---

## 8. Scalability Considerations

| Aspect | Strategy |
|--------|----------|
| Backend | Stateless, horizontal scaling via replicas |
| AI Engine | Stateless, can scale independently |
| Database | PostgreSQL with connection pooling for production |
| Rate Limiting | Per-IP rate limiting via SlowAPI |

---

*Document Owner: Architecture Team*
*Last Updated: 2026-03-07*
