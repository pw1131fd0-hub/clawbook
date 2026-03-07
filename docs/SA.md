# 🦞 Lobster K8s Copilot - 系統架構文件 (SA)

> **Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2026-03-07

---

## 1. 系統概觀 (System Overview)

Lobster K8s Copilot 採用 **分層式架構 (Layered Architecture)**，將系統分為 Frontend、Backend、AI Engine 三個主要模組。

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[🌐 Web Browser]
    end

    subgraph "Frontend (React)"
        Dashboard[Dashboard Page]
        PodList[PodList Component]
        DiagnosePanel[DiagnosePanel Component]
        YAMLEditor[YAMLCodeEditor Component]
    end

    subgraph "Backend (FastAPI)"
        API[API Gateway]
        subgraph "Controllers"
            PodCtrl[Pod Controller]
            DiagnoseCtrl[Diagnose Controller]
            YamlCtrl[YAML Controller]
        end
        subgraph "Services"
            PodSvc[Pod Service]
            DiagnoseSvc[Diagnose Service]
            YamlSvc[YAML Service]
        end
        subgraph "Repositories"
            DiagnoseRepo[Diagnose Repository]
        end
        DB[(SQLite/PostgreSQL)]
    end

    subgraph "AI Engine"
        Diagnoser[AI Diagnoser]
        subgraph "Analyzers"
            Ollama[Ollama Analyzer]
            OpenAI[OpenAI Analyzer]
            Gemini[Gemini Analyzer]
        end
    end

    subgraph "External Systems"
        K8sAPI[Kubernetes API Server]
        OllamaServer[Ollama Server]
        OpenAIAPI[OpenAI API]
        GeminiAPI[Gemini API]
    end

    Browser --> Dashboard
    Dashboard --> PodList
    Dashboard --> DiagnosePanel
    Dashboard --> YAMLEditor

    PodList --> API
    DiagnosePanel --> API
    YAMLEditor --> API

    API --> PodCtrl
    API --> DiagnoseCtrl
    API --> YamlCtrl

    PodCtrl --> PodSvc
    DiagnoseCtrl --> DiagnoseSvc
    YamlCtrl --> YamlSvc

    DiagnoseSvc --> DiagnoseRepo
    DiagnoseRepo --> DB

    DiagnoseSvc --> Diagnoser
    YamlSvc --> Diagnoser

    Diagnoser --> Ollama
    Diagnoser --> OpenAI
    Diagnoser --> Gemini

    PodSvc --> K8sAPI
    Ollama --> OllamaServer
    OpenAI --> OpenAIAPI
    Gemini --> GeminiAPI
```

---

## 2. 部署架構 (Deployment Architecture)

### 2.1 單體部署模式 (Monolithic)

```mermaid
graph LR
    subgraph "Docker Container"
        subgraph "Lobster Pod"
            FE[Frontend Static Files]
            BE[Backend FastAPI]
            FE --> BE
        end
    end

    subgraph "External"
        K8s[Kubernetes Cluster]
        LLM[LLM Provider]
        DB[(Database)]
    end

    BE --> K8s
    BE --> LLM
    BE --> DB

    User[👤 User] --> FE
```

### 2.2 微服務部署模式 (Microservices)

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Lobster Namespace"
            Ingress[Ingress Controller]
            
            subgraph "Frontend Deployment"
                FE1[Frontend Pod 1]
                FE2[Frontend Pod 2]
            end
            
            subgraph "Backend Deployment"
                BE1[Backend Pod 1]
                BE2[Backend Pod 2]
            end
            
            subgraph "AI Engine Deployment"
                AI1[AI Engine Pod]
            end
            
            FESVC[Frontend Service]
            BESVC[Backend Service]
            AISVC[AI Engine Service]
            
            PG[(PostgreSQL)]
        end
    end

    User[👤 User] --> Ingress
    Ingress --> FESVC
    FESVC --> FE1
    FESVC --> FE2
    
    FE1 --> BESVC
    FE2 --> BESVC
    BESVC --> BE1
    BESVC --> BE2
    
    BE1 --> PG
    BE2 --> PG
    
    BE1 --> AISVC
    BE2 --> AISVC
    AISVC --> AI1
```

---

## 3. 模組架構 (Module Architecture)

### 3.1 Backend 模組

```
backend/
├── main.py                 # FastAPI 進入點 + Middleware
├── database.py             # SQLAlchemy 連線設定
├── utils.py                # 敏感資料遮罩、驗證工具
├── api/
│   └── v1/
│       └── router.py       # API v1 路由聚合
├── controllers/            # HTTP 請求處理層
│   ├── pod_controller.py
│   ├── diagnose_controller.py
│   └── yaml_controller.py
├── services/               # 商業邏輯層
│   ├── pod_service.py
│   ├── diagnose_service.py
│   └── yaml_service.py
├── repositories/           # 資料存取層
│   └── diagnose_repository.py
└── models/
    ├── schemas.py          # Pydantic Request/Response Models
    └── orm_models.py       # SQLAlchemy ORM Models
```

### 3.2 AI Engine 模組

```
ai_engine/
├── main.py                 # Standalone FastAPI (微服務模式)
├── diagnoser.py            # 多模型路由器
├── analyzers/
│   ├── base_analyzer.py    # 抽象基底類別
│   ├── ollama_analyzer.py  # Ollama 本地模型
│   ├── openai_analyzer.py  # OpenAI GPT
│   └── gemini_analyzer.py  # Google Gemini
└── prompts/
    └── k8s_prompts.py      # Prompt 模板
```

### 3.3 Frontend 模組

```
frontend/
├── src/
│   ├── App.js              # 主應用元件
│   ├── index.js            # React 進入點
│   ├── components/
│   │   ├── PodList.js      # Pod 列表元件
│   │   ├── DiagnosePanel.js # AI 診斷面板
│   │   └── YAMLCodeEditor.js # Monaco 編輯器
│   ├── pages/
│   │   └── Dashboard.js    # 主頁面
│   ├── hooks/
│   │   └── useK8sData.js   # K8s 資料 Hook
│   └── utils/
│       └── api.js          # API 客戶端
└── public/
    └── index.html
```

---

## 4. 資料流程 (Data Flow)

### 4.1 Pod 診斷流程

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant K8sAPI
    participant AIEngine
    participant Database

    User->>Frontend: 點擊 Diagnose 按鈕
    Frontend->>Backend: POST /api/v1/diagnose/{pod_name}
    
    Backend->>K8sAPI: kubectl describe pod
    K8sAPI-->>Backend: Pod details
    
    Backend->>K8sAPI: kubectl logs
    K8sAPI-->>Backend: Pod logs
    
    Backend->>Backend: mask_sensitive_data()
    
    Backend->>AIEngine: diagnose(context)
    AIEngine->>AIEngine: Local-First routing
    
    alt Ollama Available
        AIEngine->>Ollama: POST /api/generate
        Ollama-->>AIEngine: AI response
    else OpenAI Available
        AIEngine->>OpenAI: POST /chat/completions
        OpenAI-->>AIEngine: AI response
    else Gemini Available
        AIEngine->>Gemini: POST /generateContent
        Gemini-->>AIEngine: AI response
    end
    
    AIEngine-->>Backend: DiagnoseResult
    
    Backend->>Database: INSERT diagnose_history
    Database-->>Backend: OK
    
    Backend-->>Frontend: DiagnoseResponse
    Frontend-->>User: 顯示診斷結果
```

### 4.2 YAML 掃描流程

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant AIEngine

    User->>Frontend: 貼上 YAML 並點擊 Scan
    Frontend->>Backend: POST /api/v1/yaml/scan
    
    Backend->>Backend: yaml.safe_load_all()
    Backend->>Backend: 檢查 Anti-Pattern Rules
    
    alt 發現問題
        Backend->>AIEngine: 請求 AI 修復建議
        AIEngine-->>Backend: AI suggestions
    end
    
    Backend-->>Frontend: YamlScanResponse
    Frontend-->>User: 顯示問題清單 + AI 建議
```

---

## 5. 安全架構 (Security Architecture)

```mermaid
graph TB
    subgraph "Security Layers"
        L1[Layer 1: API Gateway]
        L2[Layer 2: Authentication]
        L3[Layer 3: Rate Limiting]
        L4[Layer 4: Input Validation]
        L5[Layer 5: Data Masking]
        L6[Layer 6: Security Headers]
    end

    Request[HTTP Request] --> L1
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    L5 --> L6
    L6 --> Response[HTTP Response]
```

### 5.1 安全機制

| 機制 | 實作方式 |
|------|----------|
| **認證** | API Key via `Authorization: Bearer` 或 `X-API-Key` header |
| **授權** | LOBSTER_API_KEY 環境變數控制 |
| **Rate Limiting** | SlowAPI (IP-based) |
| **輸入驗證** | Pydantic validators + K8S_NAME_RE |
| **資料遮罩** | 多重正規表達式過濾敏感資訊 |
| **安全 Headers** | SecurityHeadersMiddleware |
| **CORS** | 白名單模式 (ALLOWED_ORIGINS) |

### 5.2 敏感資料處理

```mermaid
graph LR
    subgraph "Before Masking"
        Raw[K8s Logs/Describe]
    end
    
    subgraph "Masking Patterns"
        P1[PASSWORD=***]
        P2[API_KEY=***]
        P3[TOKEN=***]
        P4[Bearer ***]
        P5[ghp_***]
        P6[SSH Private Key]
    end
    
    subgraph "After Masking"
        Masked[Sanitized Text]
    end
    
    Raw --> P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> Masked
    Masked --> LLM[Send to LLM]
```

---

## 6. 可擴展性設計 (Scalability)

### 6.1 水平擴展

- **Frontend**: 可透過 K8s Deployment replicas 水平擴展
- **Backend**: 無狀態設計，可水平擴展
- **Database**: 使用 PostgreSQL 支援連接池

### 6.2 AI Provider 擴展

```python
# 新增 AI Provider 只需實作 BaseAnalyzer
class BaseAnalyzer(ABC):
    @property
    @abstractmethod
    def model_name(self) -> str: ...
    
    @abstractmethod
    def analyze(self, prompt: str) -> str: ...
    
    def is_available(self) -> bool: ...
```

---

## 7. 技術決策記錄 (ADR)

### ADR-001: 選擇 FastAPI 作為 Backend Framework

- **狀態**: 已採納
- **原因**: 原生 async 支援、自動 OpenAPI 文件、Pydantic 整合
- **替代方案**: Flask, Django REST Framework

### ADR-002: Local-First AI 策略

- **狀態**: 已採納
- **原因**: 降低 API 成本、減少延遲、支援離線環境
- **替代方案**: Cloud-Only

### ADR-003: 分層架構 (Controller-Service-Repository)

- **狀態**: 已採納
- **原因**: 職責分離、易於測試、便於維護
- **替代方案**: 單層式 MVC

---

## 8. 監控與可觀測性 (Observability)

| 類型 | 工具 | 說明 |
|------|------|------|
| **Logging** | Python logging | 結構化日誌 |
| **Health Check** | `GET /` | 回傳版本與狀態 |
| **K8s Probe** | `/api/v1/cluster/status` | 檢查 K8s 連線 |

---

*文件建立日期：2026-03-07*  
*撰寫者：System Architect (Lobster Team)*
