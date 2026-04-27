# Foundry Local Model Catalog — Code Sample Context

> This document contains all gathered context for the Model Catalog code sample deliverable.
> Read this at the start of each working session to have full background.

---

## 1. Origin: The Gartner Ask

### What Happened
Microsoft participated in the **2025 Gartner Distributed Hybrid Infrastructure (DHI) Magic Quadrant** review. During evaluation, Gartner flagged that Azure Local lacked **concrete, developer-ready examples** — the architecture and messaging were strong, but developers couldn't see *"how this actually works."*

### How It Was Translated Internally
- An Azure Local PM emailed Inbal Sagiv and Vivek N Darera: *"per a Gartner suggestion, I am requesting our docs team include a page on the Azure Local docs mentioning 'deploy AI workloads' that will link out to pages like the AI Video Indexer Arc extension page and Edge RAG"*
- This triggered two workstreams:
  1. **Docs hub page** — "Deploy AI workloads on Azure Local" (User Story 551227 in msft-skilling org)
  2. **Code samples program** — Epic #37001867

### Internal Risk Context
In PM Sync discussions, concern was raised: *"Re-engaging Gartner next year with the same story and no customers would raise red flags."* This reflects analyst-driven pressure for customer proof points and working demos.

### What We Don't Have
- ❌ The original Gartner report/slide/questionnaire has not been found
- ❌ No direct Gartner analyst quote — all references are leadership's translation
- ❓ Unclear what exactly happens on May 1 (Gartner submission? briefing? internal milestone?)

---

## 2. The Two-Pager: "Code Samples at Scale"

**Author:** Jonathan Schtechel | **Date:** February 2026 | **Status:** Ready for Review
**Location:** [SharePoint](https://microsofteur.sharepoint.com/:w:/t/ArcenabledAIWorkloads/IQC42nEO4v9jQoHykqufq1_ZAeqbjog2rc3nynZK9GNtlTg?e=wkPbtm)

### Goal
Establish a cross-product code samples program that delivers polished, working examples for Video Indexer, Agentic RAG, and Foundry Local, with a repeatable pipeline to keep producing them.

### Key Decisions
- **GitHub as single source of truth** — every sample lives in a repo with README, prerequisites, clone-configure-run experience
- **Other channels are amplifiers** — blog posts, Learn Samples Browser, Foundry Templates
- **Explicitly out of scope:** Foundry Templates as primary format
- **Six-stage pipeline:** Identify → Prioritize → Build → Review → Publish → Demo

### Foundry Local Candidates (from two-pager)
| Priority | Scenario | Customer Outcome |
|----------|----------|------------------|
| P0 | Basic chat app setup | End-to-end chat app running on Foundry Local |
| P0 | K8s deployment scripts | Production-grade Kubernetes deployment with minimal config |
| P0 | Standardized installation and packaging | Consistent clone-configure-run experience across all samples |

### Success Indicators
- Three published, polished code samples shipped — one per domain
- At least one includes an accompanying blog post
- A documented, repeatable pipeline from scenario identification through publication
- A prioritized backlog of next-up scenarios

### Reviewer Comments (February 2026)
| Reviewer | Comment | Implication |
|----------|---------|-------------|
| **Inbal Sagiv** | Tagged Vivek & Kim Lam: *"ensure we are well covered in the AI context for Gartner"* | Confirms Gartner is the driver |
| **Moran Assaf** | *"Which chat app? What does 'end to end on foundry local' mean? Needs clarification"* | Samples must be crystal clear on what they demonstrate |
| **Moran Assaf** | *"This includes the conversational UI? (it should)"* | Chat UI expected as part of the program |
| **Carmel Zolkov** | *"Maybe also BYOM + GenAI model working together on 1 GPU?"* | Future scenario to track |
| **Ika Bar-Menachem** | *"List is prioritized?"* | Priority numbering in the table answers this |
| **Omer Haimovich** | *"Consider a tutorial video"* / **Inbal:** *"+1"* | Tutorial video expected alongside samples |
| **Inbal Sagiv** | *"Let's add with MCP to SharePoint and Exchange"* | Additional scenario for the backlog |
| **Gal Mitrani** | *"This work is already in progress this semester"* | Some VI-related work was already underway |

---

## 3. ADO Work Items

### Hierarchy
```
Objective #26903319 — "AI at the Edge for Sovereign and Industrial" (Inbal Sagiv)
  └─ Epic #37001867 — "[Foundry Local] Cross-solutions Code Samples" (Jonathan)
       ├─ Feature #37341949 — Model Catalog              ⏰ May 1 (Gartner)  ← THIS DELIVERABLE
       ├─ Feature #37341951 — Agents on Azure Local       ⏰ May 1 (Gartner)
       ├─ Feature #37341950 — Chat UI + MCP + RAG         ⏰ June 1 (Build)
       ├─ Feature #37341953 — K8s Deployment Scripts       (no deadline)
       └─ Feature #37341954 — Standardized Packaging       (no deadline)
```

### Epic #37001867 Description
> *"Deliver polished, published code samples for Foundry Local as part of the cross-product code samples program. Each sample provides a working, clone-configure-run reference that shortens the customer path from POC to production."*

### Inbal's Directive (March 30, 2026)
Comment on Epic #37001867:
> *"@Jonathan Schtechel we should have here 3 features:*
> *Time sensitive:*
> *1. Code sample for Foundry Local model catalog - May 1st (Gartner)*
> *2. Code sample with chat UI, custom MCP and agentic RAG - June 1st (Build)*
> *3. Agents on AzLocal - could be e.g. with VI - May 1st. (Gartner)*
>
> *No time sensitive:*
> *4. P0 — K8s deployment scripts*
> *5. P0 — Standardized installation and packaging*
>
> *All should be defined as features on you. Are we aligned?"*

### Feature #37341949 Status
- **Description:** "Content TBD" — needs acceptance criteria
- **State:** New
- **Area Path:** Chat UI
- **Iteration:** Q4 FY26

---

## 4. Existing Code Sample Repos (Landscape)

### Official Microsoft Repos
| Repo | Description | Status |
|------|-------------|--------|
| **[microsoft/Foundry-Local](https://github.com/microsoft/Foundry-Local)** | Main product repo (2.1K ⭐) — includes built-in samples | ✅ Active |
| **[microsoft/foundry-local-samples](https://github.com/microsoft/foundry-local-samples)** | Dedicated samples repo | ❌ Archived & private |
| **[microsoft/foundry-local-on-windowsserver-samples](https://github.com/microsoft/foundry-local-on-windowsserver-samples)** | Windows Server samples (C#) | ✅ Active |
| **[microsoft/Build25-LAB329](https://github.com/microsoft/Build25-LAB329)** | Fine-tuning/distillation lab | ✅ Active |
| **[microsoft/local-email-agent](https://github.com/microsoft/local-email-agent)** | Email agent (Python + MCP) | ✅ Active |

### Azure-Samples
| Repo | Description |
|------|-------------|
| **[Azure-Samples/foundry-azure-local-chat](https://github.com/Azure-Samples/foundry-azure-local-chat)** | Chat UI for edge/sovereign/hybrid — **closest sibling repo** |

### Key Decisions Needed
- Does this sample live in `Azure-Samples` (new repo or alongside `foundry-azure-local-chat`), or standalone?
- Should it follow the same structure as `foundry-azure-local-chat`?

---

## 5. Foundry Local Model Catalog — Technical Context

### What the Model Catalog Does
The catalog is dynamic — it syncs from the Azure AI Foundry catalog API (daily via CronJob + on operator install). The docs show **25 models** in the ConfigMap example.

### Key Commands
```bash
# Query the live catalog
kubectl get cm foundry-local-catalog -n foundry-local-operator -o json \
  | jq -r '.data."catalog.json"' \
  | jq -r '["ALIAS","DEVICE","SIZE","MODEL_ID"], (.models[] | [.alias, ...]) | @tsv' \
  | column -t
```

### Models Explicitly Named in Docs
- **Phi-4-generic-cpu** (CPU)
- **Phi-4-cuda-gpu** (GPU)
- Each model has CPU and/or GPU variants with ONNX execution providers

### Catalog Architecture
- Syncs from Azure AI Foundry catalog API automatically
- Daily CronJob sync picks up newly added models
- Manual sync can be triggered
- Supports **Bring Your Own Model (BYO)** packaged as OCI image

### Documentation Source
- Private GitHub repo: [FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local)
- Use the `foundry-local` Copilot CLI skill to fetch latest docs

---

## 6. Stakeholders

| Person | Role | Relevance |
|--------|------|-----------|
| **Inbal Sagiv** | Manager | Set requirements, deadlines, owns parent objective, approves deliverables |
| **Vivek N Darera** | Reviewer | Tagged on two-pager for Gartner coverage review |
| **Kim Lam** | Reviewer | Tagged on two-pager for Gartner coverage review |
| **Moran Assaf** | PM | Asked for scope clarification on chat app / conversational UI |
| **Ika Bar-Menachem** | Reviewer | Reviewed two-pager |
| **Carmel Zolkov** | Reviewer | Suggested BYOM + GenAI scenario |
| **Omer Haimovich** | PM | Suggested tutorial video (Inbal +1'd) |
| **Gal Mitrani** | Contributor | Last modified two-pager, noted work already in progress |
| **Yonit Hoffman** | PM | Discussed scope on epic (chat UI / model work) |
| **Liran Lyabock** | PM | Involved in scope clarification on epic |
| **Adam Sarsony** | Engineering | Owns Azure Local SFF epic (#36496518) |
| **Nitzan Haimovich** | Engineering | Works on Foundry Local integration and pipelines |

---

## 7. Chronological Timeline

| Date | Event | Source |
|------|-------|--------|
| Late 2025 | Gartner DHI MQ engagement; feedback flags missing examples | PM Sync Teams thread |
| Early 2026 | Azure Local PM requests docs page "per a Gartner suggestion" | User Story 551227 |
| Feb 2026 | "Code Samples at Scale" two-pager authored and reviewed | SharePoint doc |
| Mar 5, 2026 | Epic #37001867 created | ADO |
| Mar 10, 2026 | AI workloads doc task drafted for tech writer | Copilot session |
| Mar 19, 2026 | Scope discussion on epic (Yonit, Liran, Jonathan) | Epic comments |
| Mar 30, 2026 | Inbal's directive: 5 features with Gartner/Build deadlines | Epic comment #51958271 |
| Mar 31, 2026 | All 5 features created (#37341949–37341954) | ADO |
| Apr 23, 2026 | Work begins on Model Catalog sample | This session |
