# Codebook

Each recommendation in `data/units.csv` was coded for **type** and **stance**. Each withdrawal was coded for its **reason**. Coders saw the recommendation, its heading and any example summary. They did not see other versions of it.

## 1. Type

Ask one question: **would this advice be unnecessary or inappropriate if it were addressed to a competent human colleague?**

- **Yes** → machine-specific accommodation (A1, A2 or A3). The advice compensates for an assumption about the model.
- **No** → general communication (C). The advice gives information that any competent partner needs.
- **Not about what to write in a prompt** → excluded (for example, parameters, tools, message roles, multiple calls, model choice, pricing).

The three forms of machine-specific accommodation are a closed list. Advice counts as A only if it matches one of these:

| Code | Form | Assumption about the model | Includes |
|---|---|---|---|
| **A1** | Thinking instructions | It cannot reason well on its own | "Think step by step"; reason before answering; think carefully; use thinking tags; set how deeply or how much to think; write out reasoning to improve performance; split a task into mechanical steps *because* the model cannot do it otherwise |
| **A2** | Emphasis and continuation | It reads too literally and lacks flexibility | Capital letters, IMPORTANT, repetition, forceful wording; repeating an instruction every few turns; putting text last *because* the model forgets; prefilling the answer or an output prefix for the model to continue |
| **A3** | Persona and motivation | It responds to social cues like a person | A role given to improve performance or with no stated purpose; tips, threats, praise, "this is very important to me" |

**C (general communication)** covers everything else about writing a prompt. Examples are stating the task and its purpose, giving background material, structuring the prompt, specifying the form of the answer and giving examples.

**Rules for common cases**

| Advice | Code |
|---|---|
| Give examples (few-shot), including examples of reasoning | C |
| Where to place content in the prompt | C; A2 if the stated reason is that the model forgets |
| Write instructions as numbered steps | C; A1 if the stated reason is that the model cannot do it otherwise |
| Give the model a role | C if it defines a job or a tone; A3 if it is meant to improve performance or has no stated purpose |
| Ask the model to show its reasoning | C if it is for the user to read or check; A1 if it is meant to improve performance or has no stated purpose |
| Ask the model to check its own work | C |

**Uncertain.** When a coder could not decide between A and C, the recommendation was coded C and flagged (`a1_or_c`, `a2_or_c`, `a3_or_c`). A robustness check recounts these as A.

## 2. Stance

| Code | Meaning |
|---|---|
| **do** | The guide tells users to use the technique |
| **dont** | The guide tells users not to use it, or says it is no longer needed, does not work or is not supported |

Code the technique first, then the guide's attitude to it. "Reasoning models no longer need 'think step by step'" is A1 with stance dont.

## 3. Withdrawals

A recommendation is **withdrawn** in one of two ways:

| Form | How it is identified |
|---|---|
| **Explicit retraction** | A recommendation with stance dont. It is dated to the period it first appears. |
| **Removal without notice** | A "do" recommendation that disappears from later versions with no successor that rewrites it (`outcome` = deleted in `units.csv`). It is dated to the next period, or to the period of its retired page. |

A rewritten recommendation is not a withdrawal. Advice on a model guide that ended because a newer model's guide replaced it is not a withdrawal either.

**Reason for a retraction.** Code what the guide says. If it gives several reasons, take the first that applies in this order.

| Code | The guide says the technique |
|---|---|
| unsupported | is no longer supported by the interface, or the model will refuse it |
| backfire | makes results worse |
| ineffective | does not work or is unreliable |
| unneeded | is no longer needed because the model now does it |
| alternative | should be replaced by another prompt technique or product feature |
| unstated | (no reason given) |

A third form, **walk-back** (a rewritten recommendation that softens its earlier claim), was coded but not analyzed because the two coders did not agree well enough (Table 1 note).

## 4. Derived by script

| Quantity | Rule |
|---|---|
| Category used in analysis (`lineage_category`) | For a rewritten recommendation, the category of its earliest version, so that a rewrite does not change its type |
| What a guide taught in a period | "Do" recommendations of type A1–A3 or C in the period's current documents; the same sentence on several pages counts once |
| Share of machine-specific accommodation | A1 + A2 + A3 divided by A1 + A2 + A3 + C, in each vendor's general guide |
| Model-specific recommendation | `model_scope` is not empty |

## 5. Reliability

A second coder, who did not know the study's expectations, coded a 20% sample stratified by vendor, with likely accommodation oversampled. Both coders coded the reason for every withdrawal. Agreement is reported as Krippendorff's α (nominal) with bootstrap 95% confidence intervals (Table 1).
