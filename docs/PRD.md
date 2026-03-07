# 🦞 Lobster K8s Copilot - 產品需求文件 (PRD)

> **Version**: 1.0.0 | **Status**: MVP Complete | **Last Updated**: 2026-03-07

---

## 1. 專案概述 (Project Overview)

**Lobster K8s Copilot** 是一款專為開發者與 SRE 打造的 Kubernetes 智能輔助工具。核心理念為：

> **K8s YAML 管理 + AI 診斷**

透過 AI 技術簡化 K8s YAML 的編寫與維護，並提供自動化的故障診斷與修復建議。

| 項目 | 說明 |
|------|------|
| 專案名稱 | 🦞 Lobster K8s Copilot |
| 專案狀態 | MVP 開發完成 |
| 目標用戶 | DevOps 工程師、SRE、Kubernetes 開發者 |
| 部署模式 | 單體部署 (Backend + Frontend) 或微服務模式 |

---

## 2. 產品願景 (Product Vision)

**讓 Kubernetes 管理變得像聊天一樣簡單。**

透過 AI 賦能，達成以下目標：
- 降低 K8s YAML 編寫與維護的學習曲線
- 顯著提升故障排查的效率 (MTTR ↓ 50%)
- 主動偵測 YAML 配置中的安全與可靠性問題

---

## 3. 核心功能需求 (Functional Requirements)

### 3.1 YAML 智能管理 (YAML Master)

| ID | 功能名稱 | 說明 | 優先級 |
|----|----------|------|--------|
| FR-1.1 | **反模式偵測** | 自動掃描 YAML 中的安全性與最佳實踐問題（如 Privileged Container、缺少 Resource Limits、runAsRoot、缺少 Probe、latest tag 等） | P0 |
| FR-1.2 | **差異對比** | 跨環境 (Dev/Staging/Prod) 進行 YAML 配置對比，使用 DeepDiff 演算法 | P0 |
| FR-1.3 | **AI 修復建議** | 當偵測到問題時，透過 LLM 生成人性化的修復建議 | P1 |
| FR-1.4 | **部署預檢驗** | (未來) 在 `kubectl apply` 之前模擬對 K8s 集群的影響 | P2 |

**支援的 K8s 資源類型：**
- Deployment, DaemonSet, StatefulSet, ReplicaSet
- Pod, Job, CronJob
- Ingress (含 nginx 棄用警告)

### 3.2 AI 故障診斷 (AI Diagnoser)

| ID | 功能名稱 | 說明 | 優先級 |
|----|----------|------|--------|
| FR-2.1 | **Pod 狀態監控** | 列出所有 Pod 及其狀態，支援 namespace 過濾 | P0 |
| FR-2.2 | **自動日誌抓取** | 當 Pod 進入異常狀態時，自動抓取 `kubectl logs` 與 `kubectl describe` 資訊 | P0 |
| FR-2.3 | **根因分析** | 將異常上下文傳送至 LLM，產出結構化的故障原因分析報告 | P0 |
| FR-2.4 | **修復建議** | 提供具體的 kubectl 指令或 YAML 修改建議 | P0 |
| FR-2.5 | **診斷歷史** | 保存診斷記錄，支援查詢特定 Pod 的歷史診斷 | P1 |

**支援的 Pod 異常狀態：**
- CrashLoopBackOff
- OOMKilled
- ImagePullBackOff
- Pending (資源不足)
- Error / Failed

### 3.3 多模型 AI 支援

| ID | 功能名稱 | 說明 | 優先級 |
|----|----------|------|--------|
| FR-3.1 | **Local-First 策略** | 優先使用本地 Ollama，降低成本與延遲 | P0 |
| FR-3.2 | **Cloud Fallback** | 本地不可用時自動切換至 OpenAI 或 Gemini | P0 |
| FR-3.3 | **敏感資料過濾** | 在傳送至 LLM 前過濾 Secret、Token、密碼等敏感資訊 | P0 |

---

## 4. 非功能需求 (Non-Functional Requirements)

### 4.1 效能 (Performance)

| 指標 | 目標值 |
|------|--------|
| AI 診斷響應時間 | < 10 秒 (P95) |
| YAML 掃描響應時間 | < 1 秒 |
| Pod 列表載入時間 | < 2 秒 (100 pods) |
| 支援的 YAML 大小 | 最大 512 KB |

### 4.2 安全性 (Security)

| 需求 | 實作狀態 |
|------|----------|
| API 認證 (API Key / Bearer Token) | ✅ 已實作 |
| 敏感資料遮罩 | ✅ 已實作 |
| 安全 HTTP Headers | ✅ 已實作 |
| CORS 限制 | ✅ 已實作 |
| Rate Limiting | ✅ 已實作 |
| SSRF 防護 (URL 驗證) | ✅ 已實作 |

### 4.3 可用性 (Usability)

- 提供視覺化 Dashboard 監控叢集健康度
- 支援 Monaco Editor 進行 YAML 編輯
- 響應式設計，支援桌面與平板裝置

### 4.4 相容性 (Compatibility)

- Kubernetes 版本：1.24+
- 瀏覽器：Chrome 90+、Firefox 90+、Safari 14+、Edge 90+
- Python 版本：3.11+
- Node.js 版本：18+

---

## 5. 技術約束 (Technical Constraints)

### 5.1 技術棧

| 層級 | 技術選型 |
|------|----------|
| **Backend** | Python FastAPI (Controller-Service-Repository 架構) |
| **Frontend** | React + Tailwind CSS + Monaco Editor |
| **Database** | SQLAlchemy ORM (SQLite 開發 / PostgreSQL 生產) |
| **AI** | OpenAI API / Gemini API / Ollama (Local) |
| **K8s Client** | kubernetes-python |
| **容器化** | Docker + Docker Compose |
| **部署** | Kubernetes Deployment + Service |

### 5.2 架構原則

- **分層架構**：Controller → Service → Repository
- **Local-First AI**：優先使用本地模型，減少雲端依賴
- **敏感資料不外洩**：所有傳送至 LLM 的資料必須經過遮罩處理
- **單一職責**：每個模組只負責一件事

---

## 6. 使用者流程 (User Journey)

### 6.1 YAML 掃描流程

```
1. 使用者開啟 Dashboard
2. 點擊 "YAML Editor" 頁籤
3. 貼上或編輯 K8s YAML
4. 點擊 "Scan" 按鈕
5. 系統顯示偵測到的問題清單
6. (選填) 系統顯示 AI 修復建議
7. 使用者依建議修改 YAML
```

### 6.2 Pod 診斷流程

```
1. 使用者開啟 Dashboard
2. 系統顯示當前 K8s 叢集所有 Pod 狀態
3. 使用者點擊異常 Pod 的 "Diagnose" 按鈕
4. 系統背景收集 logs 與 describe 資訊
5. 系統將資訊傳送至 AI (經敏感資料過濾)
6. 系統顯示根因分析與修復建議
7. 使用者根據建議執行修復
```

### 6.3 YAML 差異比較流程

```
1. 使用者開啟 Dashboard
2. 點擊 "YAML Diff" 功能
3. 貼入兩份 YAML (如 dev vs prod)
4. 點擊 "Compare" 按鈕
5. 系統顯示兩份 YAML 的差異
```

---

## 7. API 端點規格 (API Specification)

| Method | Endpoint | 說明 |
|--------|----------|------|
| `GET` | `/` | API 健康檢查 |
| `GET` | `/api/v1/cluster/status` | K8s 叢集連線狀態 |
| `GET` | `/api/v1/cluster/pods` | 列出所有 Pod (可選 namespace 過濾) |
| `POST` | `/api/v1/diagnose/{pod_name}` | AI 診斷指定 Pod |
| `GET` | `/api/v1/diagnose/history` | 全部診斷歷史 |
| `GET` | `/api/v1/diagnose/history/{pod_name}` | 特定 Pod 診斷歷史 |
| `POST` | `/api/v1/yaml/scan` | YAML 靜態掃描 |
| `POST` | `/api/v1/yaml/diff` | 兩份 YAML 差異比較 |

---

## 8. 成功指標 (Success Metrics)

| 指標 | 目標 |
|------|------|
| Pod 故障診斷時間縮短 | ≥ 50% |
| YAML 問題發現率 | ≥ 90% |
| 使用者滿意度 | ≥ 4.0 / 5.0 |
| 系統可用性 (Uptime) | ≥ 99.5% |

---

## 9. 風險與緩解措施

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| LLM API 不可用 | 診斷功能中斷 | Local-First 策略 + 多雲端備援 |
| K8s 叢集連線失敗 | Pod 列表無法載入 | 優雅降級，顯示友善錯誤訊息 |
| 敏感資料洩漏 | 安全事件 | 多層過濾 + 正規表達式 + Code Review |
| YAML 解析錯誤 | 使用者體驗差 | 詳細錯誤訊息 + 行號標示 |

---

## 10. 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|----------|
| 1.0.0 | 2026-03-07 | MVP 完成，含 YAML 掃描、AI 診斷、歷史記錄 |

---

*文件建立日期：2026-03-07*  
*撰寫者：Senior PM (Lobster Team)*
