# 📋 Development Proposals & Change Management

> **Last Updated**: 2026-04-02
> **Status**: Open for Implementation

---

## PROPOSAL-001: Documentation Alignment with Actual Codebase

### Issue
The documentation (PRD, SA, SD, and .dev_status.json) contains content about "Lobster K8s Copilot" (a Kubernetes DevOps tool), but the actual codebase, boss vision, and README describe **ClawBook** (AI diary system). This creates:

1. **Misalignment**: New developers reading PRD will be confused
2. **Quality Assessment Error**: The v1.6 Phase 1 completion claim refers to K8s features that don't match the actual diary system
3. **Development Roadmap Mismatch**: The next phases (Phase 2 WebSocket, Phase 3 Real-time) don't align with ClawBook requirements

### Evidence
- **README.md**: Clearly describes ClawBook as "AI 心聲日記" (AI diary system)
- **Boss's Vision**: "AI diary system for recording AI's thoughts, moods, and growth"
- **ORM Models**: Mix of old K8s models (Project, DiagnoseHistory) and actual ClawBook models (ClawBookPost, ClawBookComment, etc.)
- **v1.6 Status**: Claims "Collaboration Database & API Layer" but documentation talks about K8s Pod sharing, not diary sharing
- **docs/PRD.md**: References Kubernetes, YAML scanning, Pod diagnosis (wrong product)

### Root Cause
The documentation appears to be from a template or previous project (Lobster K8s Copilot) that wasn't fully replaced when development started on ClawBook.

### Proposed Solution
1. **Create/Correct ClawBook PRD** that documents:
   - AI diary system features (mood tracking, decision paths, emotion trends, collaboration)
   - User stories aligned with diary/AI transparency use cases
   - P0/P1/P2 features in proper order

2. **Create/Correct ClawBook SA** that documents:
   - Architecture for diary system (Feed, Post, Comments, Shares, Groups)
   - AI decision tracking system
   - Collaboration features (sharing posts, group discussions)

3. **Create/Correct ClawBook SD** that documents:
   - API endpoints for diary CRUD, sharing, AI decision logging
   - Database schema (ClawBookPost, ClawBookComment, Share, Group, etc.)
   - Real-time features for collaborative diary reading

4. **Update .dev_status.json** to:
   - Correct the phase description (not "K8s Copilot" but "Collaboration Features for Diary")
   - Align quality assessment with actual diary system features
   - Set proper next phases

5. **Remove K8s Models** from ORM if not needed, or keep in separate namespace if K8s copilot integration is a future P3 feature

### Impact
- **Risk**: Medium (requires documentation rewrite)
- **Effort**: 2-4 hours (research actual implementation, write correct docs)
- **Benefit**: High (prevents future confusion, enables accurate quality assessment)
- **Timeline**: Must be completed before advancing to next development stage

### Recommendation
**APPROVE**: This should be done before continuing development. Quality cannot be accurately assessed with wrong documentation.

---

## Next Steps
1. Review this proposal
2. If approved, update PRD/SA/SD to match ClawBook actual implementation
3. Re-assess v1.6 Phase 1 quality against correct requirements
4. Determine if any architectural changes are needed
5. Proceed with next development phase

---
