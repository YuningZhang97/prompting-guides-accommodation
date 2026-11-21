# Replication package

**From Talking to Machines to Talking to Colleagues? How AI Vendors Revised Their Advice on Communicating with Language Models**

This folder contains the data and code behind every number, table and figure in the paper.

## Contents

| Path | What it is |
|---|---|
| `data/` | The coded dataset (CSV, English) |
| `code/reproduce.py` | One script that recomputes all results |
| `results/` | Output of the script: Figure 1, Tables 1–3, robustness checks, and the other numbers cited in the text |
| `PAPER_MAP.md` | Where each claim in the paper comes from: result file, code and data |
| `codebook.md` | How each recommendation was coded |
| `segmentation_rules.md` | How the guides were collected and divided into recommendations |

## How to run

```
pip install matplotlib
python code/reproduce.py
```

The script reads only `data/` and writes to `results/`. It needs Python 3.10 or later. Apart from the figure, it uses only the standard library.

## The data

The study covers the official prompting guides of OpenAI (OA), Anthropic (AN) and Google (GG) from the second half of 2022 (2022H2) to 2026H2. Each half-year is one period.

| File | One row per | Key columns |
|---|---|---|
| `documents.csv` | page in a period (126 rows) | `layer` general guide or model guide; `role` current (still online at the end of the period) or retired (taken down during it); `snapshot_url` the archived copy used; `source` wayback or github |
| `units.csv` | unit (832 rows; 35 coded out of scope in `codes.csv`, leaving 797 recommendations) | `text` the recommendation as written in the guide; `first_period`, `last_period`; `revised_from` the earlier version it rewrites; `dup_group` the same sentence on several pages of one period; `model_scope` the named models it applies to (empty = all models); `outcome` active, revised, deleted, ended_with_model_page or uncertain |
| `occurrences.csv` | recommendation in a document | which documents and periods each recommendation appears in |
| `codes.csv` | recommendation | first coder: `category` (A1, A2, A3, C, excluded), `stance` (do, dont), `uncertain` (a1_or_c, a2_or_c, a3_or_c), `lineage_category` (the category used in analysis, see codebook) |
| `codes_coder2.csv` | recommendation in the reliability sample (160 rows) | second coder, same columns |
| `withdrawals.csv` | explicit retraction or revised recommendation (211 rows) | first coder: `reason` for a retraction; `walk_back` for a revision |
| `withdrawals_coder2.csv` | same rows | second coder |
| `segmentation_coder1.csv`, `segmentation_coder2.csv` | candidate text block in the segmentation test (182 rows) | `decision` include or skip |
| `colleague_sentences.csv` | guide sentence that compares the model to a person | found by keyword search in the full guide texts; source of Table 3 |
| `reasoning_models.csv` | vendor | release date of each vendor's first reasoning model, with source |

Categories: **A1** thinking instructions, **A2** emphasis and continuation, **A3** persona and motivation. A1–A3 together form **machine-specific accommodation**. **C** is general communication.

## What is not included

The full text of the guide pages is not included because the vendors hold the copyright. Each document's archived copy can be opened from `snapshot_url` in `documents.csv`. Table 3 is therefore built from `colleague_sentences.csv`, which the original pipeline extracted from the full texts.

The collection and segmentation pipeline (web archive download, AI-drafted segmentation and its checks) is kept in the main repository under `scripts/`. It is not needed to reproduce the results.
