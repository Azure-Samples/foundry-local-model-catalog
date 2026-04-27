# Foundry Local Model Catalog — Code Sample Plan

> **Feature:** #37341949 | **Deadline:** May 1, 2026 (Gartner) | **Owner:** Jonathan Schtechel
>
> Start each session with: *"Read ~/Desktop/foundry-local-model-catalog/PLAN.md and CONTEXT.md, then let's continue"*

---

## Current Status

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Define scope & requirements | ✅ Done | Completed Apr 23 |
| 2. Brainstorm & design | ✅ Done | Design locked Apr 23 |
| 3. Implement code sample | ✅ Done | Code written Apr 23 |
| 4. Review code sample | 🔄 In progress | Code reviewed & polished Apr 26; ready for cluster test |
| 5. Write blog/article | 🔲 Not started | Post-May 1 deliverable |
| 6. Publish & amplify | 🔲 Not started | Depends on Phase 5 |

---

## Phase 1: Define Scope & Requirements

**Goal:** Lock down exactly what the sample demonstrates and where it lives.

- [ ] Clarify what "model catalog" means in this sample:
  - Query available models?
  - Deploy a model from the catalog?
  - Run inference against a deployed model?
  - All three (end-to-end)?
- [ ] Review Foundry Local on Azure Local documentation for catalog capabilities
  - Use the `foundry-local` Copilot CLI skill to fetch latest docs
- [ ] Review existing repos for overlap:
  - `Azure-Samples/foundry-azure-local-chat`
  - `microsoft/Foundry-Local` (built-in samples)
  - `microsoft/foundry-local-on-windowsserver-samples`
- [ ] Decide repo location (new Azure-Samples repo? subfolder? standalone?)
- [ ] Update Feature #37341949 description with acceptance criteria
- [ ] Confirm Azure Local cluster + Foundry Local access for testing

---

## Phase 2: Brainstorm & Design ✅

**Goal:** Design the sample structure before writing code.

- [x] Define target audience → **Developers/MLOps engineers deploying AI on Azure Local (K8s-based)**
- [x] Choose language/framework → **Python + `kubernetes` client library + OpenAI SDK**
- [x] Design sample structure → **Single script + README (lean, tutorial-style)**
- [x] Align with Feature #37341954 → **clone→configure→run experience**
- [x] Document what the sample demonstrates end-to-end → **Full catalog lifecycle**

### Design Decisions (Locked Apr 23)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Scope** | Full catalog lifecycle: query → deploy → infer → cleanup | Fills gap — no existing sample does this on Azure Local |
| **Language** | Python + `kubernetes` client + `openai` SDK | Standard for K8s/AI dev, matches Foundry Local ecosystem |
| **Repo** | New `Azure-Samples/foundry-azure-local-model-catalog` | Parallel with `foundry-azure-local-chat` sibling |
| **Format** | Single `catalog_sample.py` + README | Lean, developer-ready, easy to clone→run |

### Repo Structure

```
foundry-azure-local-model-catalog/
├── README.md                    # Prerequisites, setup, usage, architecture
├── catalog_sample.py            # End-to-end: query → deploy → infer → cleanup
├── requirements.txt             # kubernetes, openai
├── LICENSE.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SECURITY.md
└── .gitignore
```

### What the Sample Demonstrates (E2E Flow)

1. **Query the catalog** — Read the `foundry-local-catalog` ConfigMap, list available models with alias/device/size
2. **Deploy a model** — Create a `ModelDeployment` CR from a catalog entry (Phi-4 CPU or GPU)
3. **Wait for ready** — Poll the ModelDeployment until state = `Running`
4. **Run inference** — Call the OpenAI-compatible `/v1/chat/completions` endpoint using the auto-generated API key
5. **Clean up** — Delete the ModelDeployment (optional, prompted)

### Gap Analysis (Why This Is Unique)

| Existing Sample | What It Covers | What's Missing |
|----------------|----------------|----------------|
| `microsoft/Foundry-Local/samples/python/` | Chat, embeddings, tool calling on **Windows desktop** | No K8s, no catalog, no Azure Local |
| `Azure-Samples/foundry-azure-local-chat` | Chat UI on AKS (TypeScript/React) | No catalog operations, different language |
| `microsoft/foundry-local-on-windowsserver-samples` | C# samples for Windows Server | Different platform, language |
| **This sample** | **Full catalog lifecycle on Azure Local (Python)** | — |

---

## Phase 3: Implement

**Goal:** Write the code and validate it works.

- [ ] Write the code following clone→configure→run principles
- [ ] Create comprehensive README
- [ ] Add LICENSE, CONTRIBUTING.md per Microsoft open-source standards
- [ ] Test on actual Azure Local infrastructure
- [ ] Iterate and refine

---

## Phase 4: Review

**Goal:** Get the sample reviewed and approved by May 1.

- [x] Push to private repo for look-and-feel review → [Schtechel/foundry-azure-local-model-catalog](https://github.com/Schtechel/foundry-azure-local-model-catalog)
- [x] Code review & polish (Apr 26) — fixed 5 blocking issues:
  - Python 3.9 compat (`from __future__ import annotations`)
  - GPU resource key (`nvidia.com/gpu` instead of bare `gpu`)
  - Guaranteed cleanup on failure (`try/finally`)
  - Safe deployment reuse on 409 (validates model/version/compute match)
  - TLS security (`--insecure` flag; verification ON by default)
  - Plus: `SampleError` exception class, RBAC docs, README polish
- [ ] Test on demo cluster (run the full lifecycle)
- [ ] Technical review (Foundry Local engineering team)
- [ ] PM review (Inbal)
- [ ] Editorial review (technical writer)
- [ ] Address feedback and iterate
- [ ] Move repo to Azure-Samples org when ready

---

## Phase 5: Write Blog/Article (Post-May 1)

**Goal:** Create accompanying content that explains and promotes the sample.

- [ ] Research Microsoft code sample blog formats and standards
- [ ] Draft article explaining the sample, its capabilities, and usage
- [ ] Include screenshots, diagrams, architecture overview
- [ ] Reference the GitHub repo as authoritative source
- [ ] Consider recording a tutorial video (per Inbal/Omer feedback)

---

## Phase 6: Publish & Amplify

**Goal:** Ship everything.

- [ ] Publish code sample to GitHub
- [ ] Publish blog to platform (Tech Community / learn.microsoft.com)
- [ ] Submit to Learn Samples Browser when stable
- [ ] Record tutorial video if bandwidth allows

---

## Open Questions (to resolve as we go)

- What exactly happens on May 1? Gartner submission, briefing, or internal milestone?
- Should the sample include BYOM (Bring Your Own Model) scenarios?
- Does Vivek or Kim Lam need to review?
- Is there a standard Microsoft code sample template we should follow?
