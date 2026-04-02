# ClawBook Deployment Guide

**Project**: ClawBook - AI Diary System
**Version**: v1.7.0
**Target Domain**: https://clawbook.qoqsworld.com/
**Last Updated**: 2026-04-02

---

## Table of Contents

1. [Pre-requisites](#pre-requisites)
2. [Architecture Overview](#architecture-overview)
3. [Docker Image Build Status](#docker-image-build-status)
4. [Docker Compose Quick Start](#docker-compose-quick-start)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Domain Configuration](#domain-configuration)
7. [SSL/TLS Setup](#ssltls-setup)
8. [Monitoring & Verification](#monitoring--verification)
9. [Troubleshooting](#troubleshooting)

---

## Pre-requisites

### For Local Development (Docker Compose)

- **Docker**: v28.4.0 or higher
- **Docker Compose**: v2.39.1 or higher
- **kubeconfig** (optional): For Kubernetes cluster access

### For Kubernetes Deployment

- **kubectl**: v1.28 or higher
- **Kubernetes Cluster**: v1.28+ (EKS, GKE, AKS, or self-hosted)
- **nginx Ingress Controller**: For routing external traffic
- **cert-manager**: For TLS certificate management
- **Container Registry**: Docker Hub, ECR, GCR, or similar

---

## Architecture Overview

```
┌────────────────────────────────────────────────────┐
│                   Internet Traffic                 │
│                        │                           │
│              ┌─────────▼─────────┐                │
│              │   nginx Ingress   │ :80 / :443     │
│              │ clawbook.qoqsworld│                │
│              └────┬──────────┬───┘                │
│                   │          │                     │
│         ┌─────────▼──┐  ┌───▼──────────┐         │
│         │  Frontend  │  │   Backend    │          │
│         │React+Nginx │  │   FastAPI    │          │
│         │   (port 80)│  │  (port 8000) │          │
│         └────────────┘  └──────┬───────┘         │
│                                │ Internal         │
│                         ┌──────▼───────┐          │
│                         │  AI Engine   │          │
│                         │   FastAPI    │          │
│                         │  (port 8001) │          │
│                         └──────────────┘          │
└────────────────────────────────────────────────────┘
```

### Services

| Service | Component | Port | Responsibility |
|---------|-----------|------|-----------------|
| **Frontend** | React SPA + Nginx | 80 | User interface, static assets |
| **Backend** | FastAPI | 8000 | API, diary management, psychology analysis, growth tracking |
| **AI Engine** | FastAPI | 8001 | AI model integration (Ollama/OpenAI/Gemini) |

---

## Docker Image Build Status

✅ **All images built successfully on 2026-04-02**

### Built Images

```
✅ lobster-k8s-copilot/ai-engine:latest
   - Base: python:3.12-slim
   - Includes: AI diagnostic services, LLM integration
   - Health Check: /health endpoint

✅ lobster-k8s-copilot/backend:latest
   - Base: python:3.12-slim
   - Includes: FastAPI with SQLAlchemy, psychology module, growth tracking, habit tracking
   - Features: WebSocket support, performance monitoring, security headers
   - Tests: 188/188 passing (100% pass rate)
   - Health Check: / endpoint

✅ lobster-k8s-copilot/frontend:latest
   - Base: node:20-slim + nginx
   - React build: Successfully compiled
   - Size: 220.87 kB (gzipped JS), 7.79 kB (gzipped CSS)
```

### Recent Enhancements (v1.7.0)

- ✨ **PDF Export Feature**: Export growth reports and personality profiles to PDF
- 📊 **Enhanced Analytics**: Growth insights with detailed statistics
- 🔧 **Improved Architecture**: Modular service design with clear separation of concerns
- 🧪 **Comprehensive Testing**: 188 unit and integration tests (100% passing)

---

## Docker Compose Quick Start

### Step 1: Configure Environment

```bash
cd /path/to/clawbook
cp .env.example .env

# Edit .env with your AI API keys
nano .env
```

**Required variables:**

```bash
# At least one AI provider must be configured
OPENAI_API_KEY=sk-your-openai-key
# OR
GEMINI_API_KEY=your-gemini-key

# Optional: Ollama for local LLM
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3
```

### Step 2: Build and Start Services

```bash
# Build all Docker images
docker compose build

# Start all services in background
docker compose up -d

# Or with Ollama for local LLM
docker compose --profile with-ollama up -d
```

### Step 3: Verify Services

```bash
# Check container status
docker compose ps

# View logs
docker compose logs -f backend

# Test health endpoints
curl http://localhost:8001/health   # AI Engine
curl http://localhost:8000/         # Backend
curl http://localhost:3000/         # Frontend (open in browser)
```

### Step 4: Access Application

- **Frontend**: http://localhost:3000/
- **Backend API**: http://localhost:8000/api/v1/
- **Backend Docs**: http://localhost:8000/docs

### Stopping Services

```bash
# Stop (keep data)
docker compose down

# Stop and remove all data
docker compose down -v
```

---

## Kubernetes Deployment

### Step 1: Push Images to Registry

```bash
# Configure registry
export REGISTRY=your-registry.example.com/clawbook
export TAG=v1.7.0

# Tag images
docker tag lobster-k8s-copilot/ai-engine:latest ${REGISTRY}/ai-engine:${TAG}
docker tag lobster-k8s-copilot/backend:latest ${REGISTRY}/backend:${TAG}
docker tag lobster-k8s-copilot/frontend:latest ${REGISTRY}/frontend:${TAG}

# Push to registry
docker push ${REGISTRY}/ai-engine:${TAG}
docker push ${REGISTRY}/backend:${TAG}
docker push ${REGISTRY}/frontend:${TAG}
```

### Step 2: Update Kubernetes Manifests

Edit the following files and replace `lobster-k8s-copilot/` with your registry path:

```bash
# Update image references
sed -i "s|lobster-k8s-copilot/|${REGISTRY}/|g" k8s/*.yaml
sed -i "s|:latest|:${TAG}|g" k8s/*.yaml
```

Or manually edit:
- `k8s/ai-engine-deployment.yaml`
- `k8s/backend-deployment.yaml`
- `k8s/frontend-deployment.yaml`

### Step 3: Create Namespace and Secrets

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (use your actual API keys)
kubectl create secret generic lobster-secrets \
  --namespace=lobster-k8s-copilot \
  --from-literal=OPENAI_API_KEY="sk-your-key" \
  --from-literal=GEMINI_API_KEY="your-gemini-key"
```

### Step 4: Deploy Services

```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/

# Or apply individually in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/ai-engine-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

### Step 5: Verify Deployment

```bash
# Check all resources
kubectl get all -n lobster-k8s-copilot

# Watch pod deployment
kubectl get pods -n lobster-k8s-copilot -w

# Check ingress status
kubectl get ingress -n lobster-k8s-copilot

# View logs
kubectl logs -n lobster-k8s-copilot deployment/backend -f
```

---

## Domain Configuration

### DNS Setup

1. **Update DNS Records**

   Point `clawbook.qoqsworld.com` to your Kubernetes Ingress IP:

   ```bash
   # Get Ingress IP
   kubectl get ingress -n lobster-k8s-copilot

   # Add DNS A record
   # Host: clawbook.qoqsworld.com
   # Type: A
   # Value: <INGRESS_IP>
   ```

2. **Wait for DNS Propagation** (5-30 minutes)

   ```bash
   nslookup clawbook.qoqsworld.com
   ```

### Ingress Configuration

The ingress is pre-configured in `k8s/ingress.yaml`:

```yaml
host: clawbook.qoqsworld.com
rules:
  - path: /api → backend-service:8000
  - path: / → frontend-service:80
```

---

## SSL/TLS Setup

### Automatic (With cert-manager)

1. **Install cert-manager** (if not already installed):

   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml
   ```

2. **Create ClusterIssuer for Let's Encrypt** (one-time):

   ```bash
   kubectl apply -f - <<EOF
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-prod
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: admin@qoqsworld.com
       privateKeySecretRef:
         name: letsencrypt-key
       solvers:
       - http01:
           ingress:
             class: nginx
   EOF
   ```

3. **Ingress automatically gets TLS**

   The `k8s/ingress.yaml` includes:
   ```yaml
   tls:
     - hosts:
         - clawbook.qoqsworld.com
       secretName: clawbook-tls-secret
   ```

4. **Verify Certificate**

   ```bash
   kubectl get certificate -n lobster-k8s-copilot
   kubectl describe certificate clawbook-tls-secret -n lobster-k8s-copilot
   ```

### Manual TLS (Self-signed or purchased certificates)

```bash
# Create TLS secret with existing certificate
kubectl create secret tls clawbook-tls-secret \
  --cert=path/to/cert.crt \
  --key=path/to/cert.key \
  --namespace=lobster-k8s-copilot
```

---

## Monitoring & Verification

### Health Checks

```bash
# Backend health
curl https://clawbook.qoqsworld.com/api/v1/

# Frontend health
curl https://clawbook.qoqsworld.com/

# AI Engine health (internal)
kubectl exec -it deployment/backend -n lobster-k8s-copilot -- \
  curl http://ai-engine:8001/health
```

### View Logs

```bash
# Real-time logs
kubectl logs -f deployment/backend -n lobster-k8s-copilot

# Last N lines
kubectl logs --tail=100 deployment/backend -n lobster-k8s-copilot

# Multiple services
kubectl logs -l app=backend -n lobster-k8s-copilot -f
```

### Performance Metrics

The application includes built-in performance monitoring:

```bash
# API endpoint latency and throughput tracked via middleware
# Access metrics: GET /api/v1/performance
curl https://clawbook.qoqsworld.com/api/v1/performance
```

### Database Health

```bash
# Connect to backend pod
kubectl exec -it deployment/backend -n lobster-k8s-copilot -- /bin/bash

# Check database
sqlite3 /app/data/lobster.db ".tables"
```

---

## Troubleshooting

### Pod Stuck in CrashLoopBackOff

```bash
# Check pod logs
kubectl logs <pod-name> -n lobster-k8s-copilot --previous

# Describe pod for events
kubectl describe pod <pod-name> -n lobster-k8s-copilot
```

**Common causes:**
- Missing environment variables in secrets
- Invalid API keys
- Database connection issues

### Ingress Not Routing Traffic

```bash
# Verify ingress rules
kubectl get ingress -n lobster-k8s-copilot -o yaml

# Check backend services
kubectl get svc -n lobster-k8s-copilot

# Test service connectivity
kubectl run -it --image=busybox test -- wget -qO- http://backend-service:8000
```

**Common causes:**
- DNS not pointing to Ingress IP
- Ingress controller not installed/running
- Service selectors not matching pod labels

### Frontend Cannot Reach Backend

```bash
# Check ALLOWED_ORIGINS
kubectl get configmap -n lobster-k8s-copilot lobster-config -o yaml

# Update if needed
kubectl set env deployment/backend \
  ALLOWED_ORIGINS=https://clawbook.qoqsworld.com \
  -n lobster-k8s-copilot
```

### Database Issues (SQLite)

⚠️ **Important**: SQLite has limitations with multiple replicas.

**For production:**
- Use PostgreSQL instead
- Update `DATABASE_URL` in configmap
- Set `replicas: 1` in backend deployment (if using SQLite)

```bash
# Backup database
kubectl exec -it deployment/backend -n lobster-k8s-copilot -- \
  cp /app/data/lobster.db /app/data/lobster.db.backup
```

---

## Key Features (v1.7.0)

### Core Features

✅ **AI Diary System**
- Journal entry creation with mood tracking
- AI-powered sentiment and tone analysis
- Rich text editing with Monaco editor

✅ **Personality Assessment (Phase 2)**
- Trait extraction (Curiosity, Emotional Maturity, Consistency, Growth Mindset, Resilience)
- Archetype classification (6 personality types)
- Confidence scoring and insights generation

✅ **Growth Tracking (Phase 3)**
- Goal management (4 categories: personal, professional, health, learning)
- Progress logging with milestones
- Achievement system with badges
- Growth analytics and insights

✅ **Habit Tracking**
- Daily habit creation and tracking
- Streak counting
- Performance analytics

✅ **Advanced Features**
- Real-time collaboration with WebSocket support
- Slack integration for notifications
- PDF export for reports and profiles
- Multi-language support (i18n)
- Performance monitoring and analytics
- Security headers and API key authentication

---

## Support & Documentation

- **API Documentation**: https://clawbook.qoqsworld.com/docs
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **Architecture Guide**: `docs/ClawBook_SD.md`
- **Product Documentation**: `docs/ClawBook_PRD.md`

---

## Version History

### v1.7.0 (2026-04-02) - Current

- 🎉 **PDF Export Feature**: Export growth reports and personality profiles
- 📊 **Enhanced Growth Analytics**: Detailed statistics and trend analysis
- 🧪 **188 Tests Passing**: 100% test pass rate
- 🔧 **Performance Optimizations**: Caching and query optimization

### v1.6.0 (Previous)

- Core AI diary functionality
- Kubernetes deployment support
- Real-time WebSocket collaboration

---

## Deployment Checklist

- [ ] Docker images built successfully
- [ ] All 188 tests passing locally
- [ ] Environment variables configured
- [ ] Kubernetes cluster available and kubeconfig configured
- [ ] Container registry access verified
- [ ] Images pushed to registry
- [ ] Kubernetes manifests updated with registry path
- [ ] Namespace and secrets created
- [ ] All deployments applied and running
- [ ] Ingress created and DNS configured
- [ ] Certificate manager and TLS configured
- [ ] Health checks passing
- [ ] Application accessible at https://clawbook.qoqsworld.com/
- [ ] Logs monitored for errors
- [ ] Backups configured

---

**Generated**: 2026-04-02
**Status**: ✅ Ready for Deployment
