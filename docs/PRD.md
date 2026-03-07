# 🦞 Lobster K8s Copilot - 產品需求文件 (PRD) v2.5 (Copilot Powered Migration)

## 1. 專案概述 (Project Overview)
Lobster K8s Copilot v2.5 定位為 **「專為 GitHub Copilot 打造的 K8s 遷移插件與智庫」**。核心目標是利用 Copilot 的開發者生態位，解決 2026 年 `ingress-nginx` 退役帶來的遷移挑戰。

- **專案名稱**：Lobster K8s Copilot (Copilot Edition)
- **版本編號**：v2.5
- **更新日期**：2026-03-07
- **關鍵字**：GitHub Copilot, Ingress-to-Gateway API, AI-Driven Refactoring.

## 2. 產品願景 (Product Vision)
成為 GitHub Copilot 在 Kubernetes 領域最強的「大腦擴充」。當開發者在 VS Code 寫 YAML 時，Lobster 能主動介入並引導完成從舊時代 (Ingress) 到新時代 (Gateway API) 的代碼重構。

## 3. 核心功能需求 (Functional Requirements)

### 3.1 Copilot 深度整合 (Copilot Synergy) [NEW]
- **FR-1.1 遷移指令擴充 (@lobster /migrate)**：
  - 在 GitHub Copilot Chat 中，開發者可以輸入 `/migrate` 並選取舊版 Ingress YAML。
  - **功能**：Lobster 引擎與 Copilot 聯動，直接在編輯器生成 **Gateway API (HTTPRoute)** 的代碼建議。
- **FR-1.2 即時反模式重構 (Live Refactoring)**：
  - 當 Copilot 生成包含 `ingress-nginx` 註解 (Annotations) 的代碼時，Lobster 主動標記並提供「一鍵轉換為 Gateway API Filter」的 Quick Fix。

### 3.2 遷移專用知識庫 (Migration RAG) [NEW]
- **FR-2.1 Ingress-to-Gateway 映射字典**：
  - 建立完整的 Annotation-to-Spec 映射庫（例如：`nginx.ingress.kubernetes.io/rewrite-target` -> `HTTPRoute filter: URLRewrite`）。
- **FR-2.2 多品牌遷移路徑**：
  - 支援將 Ingress 轉換為不同 Provider 的 Gateway API 實作（如 Cilium, Envoy Gateway, Traefik）。

### 3.3 遷移後驗證 (Post-Migration Validation)
- **FR-3.1 語義對等檢查 (Semantic Equivalence Check)**：
  - AI 驗證轉換後的 Gateway API 邏輯與原有的 Ingress 規則是否完全一致，避免遷移導致的路由錯誤。

## 4. 非功能需求 (Non-Functional Requirements)
- **Context 最小化**：優化傳送給 Copilot 的 Prompt，確保在有限的 Token 預算內提供最高質量的轉換建議。
- **Developer Experience (DX)**：轉換建議必須符合開發者的編碼風格，包含清晰的註解說明「為什麼要這樣轉」。

## 5. 技術架構
- **Core Engine**: Python (FastAPI) 負責處理複雜的 YAML 邏輯轉換。
- **AI Backend**: 深度調優的 LLM Prompting，專門針對 Kubernetes 資源映射。
- **Integration Layer**: 透過 VS Code Extension API 橋接 GitHub Copilot。

## 6. 使用者流程 (User Journey)
1. 開發者在 VS Code 打開一個帶有 `ingress-nginx` 標籤的舊專案。
2. Copilot Chat 提示：「偵測到退役組件，是否執行 Lobster 遷移建議？」
3. 開發者輸入 `/migrate`。
4. Lobster 掃描專案，產出對應的 `Gateway` 與 `HTTPRoute` YAML 檔案。
5. 開發者確認並 Commit。

---
*文件更新日期：2026-03-07*
*撰寫者：小龍蝦 (Lobster AI)*
