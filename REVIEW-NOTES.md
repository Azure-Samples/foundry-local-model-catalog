# Review Notes — Open Questions for Reviewer

These items were validated against the actual Foundry Local on Azure Local cluster
(`aks-foundry-demoenv-gpu01-weu`) on April 26, 2026.

## 1. GPU resource key format — ✅ RESOLVED

**Answer:** The `ModelDeployment` CRD accepts `gpu: <integer>` in its resources spec.
The CRD schema describes it as "Number of GPUs (nvidia.com/gpu)" with min=0, max=8.
The operator translates this to `nvidia.com/gpu` in the underlying pod spec automatically.

**Our code:** `"gpu": 1` in `MODEL_PRESETS["Phi-4-generic-gpu"]` — **correct**.

## 2. Default port in ModelDeployment CRD — ✅ RESOLVED

**Answer:** The CRD's default port is `5000` (type: integer, min: 1024, max: 65535).

**Our code:** Explicitly sets `spec.port: 5000` — **correct** (redundant but safe).

## 3. Resource presets (CPU/memory values) — ✅ RESOLVED

**Answer:** CRD defaults are minimal (100m CPU, 256Mi memory) — unsuitable for real
model inference. Our presets (e.g., Phi-4 CPU: 2 CPU / 8Gi request, 4 CPU / 24Gi limit)
are appropriate for actual inference workloads.

**Validated:** Phi-4-generic-cpu deployed and ran inference successfully with our presets.

## 4. Documentation links — 🔲 OPEN

**Current:** All links to the private `FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local`
repo have been removed. A placeholder TODO comment marks where the public docs link
should go in the Resources section.

**Action needed:** Once public documentation is available, add the link to README.md
Resources section and optionally restore the "Docs Reference" column in the
"What This Sample Does" table.

---

## Issues Found & Fixed During QA (April 26, 2026)

### Issue 1: Default `--version 1` breaks out of the box (BLOCKING)
- **Root cause:** Catalog versions change over time. Phi-4-generic-cpu is at version 2.
  Hardcoding `--version 1` meant the script would fail immediately on fresh clone.
- **Fix:** Changed `--version` default to `None` (auto-detect from catalog).
  `resolve_variant()` now matches by `displayName` + compute when version is None,
  extracting the actual version from the catalog automatically.

### Issue 2: GPU preset name `Phi-4-cuda-gpu` doesn't exist (BLOCKING)
- **Root cause:** The actual GPU model in the catalog is `Phi-4-generic-gpu`, not
  `Phi-4-cuda-gpu`.
- **Fix:** Renamed `MODEL_PRESETS` key and all README/docstring references.

### Issue 3: README missing virtual environment instructions
- **Impact:** `pip install -r requirements.txt` fails on modern Python (PEP 668 /
  macOS Homebrew) without a venv.
- **Fix:** Added venv creation step to README Getting Started section.
