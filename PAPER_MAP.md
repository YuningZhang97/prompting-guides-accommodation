# Paper map

Where each number and quotation in the paper comes from. All result files are written by `code/reproduce.py`. The function named in the "Code" column produces the number.

| Paper | Claim | Result | Code | Data |
|---|---|---|---|---|
| Abstract; Method | 797 recommendations in 126 documents (832 units, 35 out of scope) | `numbers.md` › Method | `numbers()` | `units.csv`, `documents.csv` |
| Method | 104 current and 22 retired documents | `numbers.md` › Method | `numbers()` | `documents.csv` (`role`) |
| Method | OpenAI 2024H2 uses a repository copy of 25 July 2024 | — | — | `documents.csv` (`source` = github, `snapshot_time`) |
| Method; Table 1 | Segmentation α = .81 | `table1.md` row 1 | `table1()` | `segmentation_coder1.csv`, `segmentation_coder2.csv` |
| Method; Table 1 | Type, stance and reason α = .87–.95 | `table1.md` rows 2–5 | `table1()` | `codes.csv`, `codes_coder2.csv`, `withdrawals.csv`, `withdrawals_coder2.csv` |
| Abstract; 4.1; Figure 1 | Share fell at all three vendors: OpenAI 24%→3%, Anthropic 37%→9%, Google 29%→16% | `numbers.md` › 4.1; `shares.csv`; `figure1.png` | `taught()`, `share()`, `shares_and_figure()` | `occurrences.csv`, `codes.csv`, `units.csv` |
| 4.1 | Under three robustness checks (uncertain codes counted as accommodation, repeated sentences counted per page, OpenAI 2024H2 copy left out), OpenAI's and Anthropic's latest shares stay below half of their peaks | `numbers.md` › Robustness checks; `robustness.csv` | `robustness()`, `lineage()`, `taught()` | `codes.csv` (`uncertain`), `units.csv` (`revised_from`, `dup_group`), `occurrences.csv` |
| 4.1 | OpenAI 8→1 accommodation, 26→33 general; Anthropic 15→7 and 29→69; Google 5→7, general communication more than doubled in 2025H2 (17→41) | `numbers.md` › 4.1 counts; `shares.csv` | `taught()` | as above |
| 4.1 | Google withdrew only three accommodating recommendations and added new thinking instructions | `numbers.md` › 4.1 | `withdrawals()` | `units.csv` (`outcome`), `codes.csv` |
| 4.1 | Forms in 2026H2: thinking instructions 6/3/1; Google kept 4 of 5 emphasis; persona down to 1 | `numbers.md` › Forms; `shares.csv` | `taught()` | as above |
| 4.1 | 13 of 17 retractions of thinking instructions in Anthropic's 2026H2 model guides | `numbers.md` › Forms | `withdrawals()` | `codes.csv` (`stance` = dont), `units.csv` |
| 4.1 | Reasoning models: Google's share fell only in 2025H2; Anthropic stayed at 34% for a year after February 2025; OpenAI 2025H1 missing | `numbers.md` › before/after | `numbers()` | `reasoning_models.csv`, `documents.csv` |
| 4.2; Table 2 | 48 withdrawals: 27 retractions, 21 removals; 56% vs 31% explicitly retracted | `table2.md`; `numbers.md` › 4.2 | `withdrawals()`, `table2()` | `codes.csv`, `units.csv`, `occurrences.csv`, `documents.csv` |
| 4.2 | Most withdrawals came from Anthropic (41 of 48) | `numbers.md` › 4.2 | `withdrawals()` | as above |
| 4.2 | All retractions concerned thinking instructions or emphasis; persona only removed | `numbers.md` › 4.2 (by form) | `withdrawals()` | as above |
| 4.2 | More than a third gave no reason (10 of 27); unsupported and ineffective most common (5 each) | `numbers.md` › 4.2 (reasons) | `withdrawals()` | `withdrawals.csv` (`reason`) |
| Table 2 note | 25.6% vs 14.2% later removed without notice | `table2.md` note; `numbers.md` › Table 2 note | `rates_ever_taught()` | `occurrences.csv`, `units.csv` |
| 4.3; Table 3 | Anthropic's employee descriptions; OpenAI's senior and junior coworker | `table3.md` | `table3()` | `colleague_sentences.csv` |
| 4.3 | Model-specific advice in 2026H2: OpenAI 71%, Google 32%, Anthropic 12%; almost none before 2025 | `numbers.md` › 4.3 | `model_specific_share()` | `units.csv` (`model_scope`), `occurrences.csv` |
| 1; 4.2 | Prefill quotations ("a few prefilled sentences…", "are no longer supported", "should be sufficient") | — | — | `units.csv` (`text`) |
| 4.2 | "most use cases of prefill no longer require it" (explanatory sentence, not itself a recommendation) | — | — | Anthropic 2026H1–H2 prompting best-practices page; open via `snapshot_url` in `documents.csv` |
| 2 | Example quotations ("Think step-by-step", "every 3-5 user messages", "dramatically improve its performance") | — | — | `units.csv` (`text`) |

Sections 5.1–5.4 interpret these results and introduce no new numbers.
