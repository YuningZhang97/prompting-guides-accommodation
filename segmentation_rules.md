# Segmentation rules

These rules describe how the guides were collected and divided into recommendations.

## 1. Collecting the guides

- **Guide.** A page that the vendor's documentation site grouped under prompting in its navigation menu. The vendor's own menu defines what counts as its guide.
- **Period.** Half-years from 2022H2 to 2026H2 (UTC). For each page and period, the last archived copy in the Wayback Machine was used. If it had little text (under 1,500 characters), an earlier copy from the same half-year was used. GitHub copies were used only where the vendor published the guide in its official repository or where the archive had no text (OpenAI 2024H2).
- **Layer.** A guide written for a vendor's newest flagship model is a **model guide**. All other pages form the **general guide**. The two layers are analyzed separately.
- **Role.** A page still online at the end of a period is **current** and counts toward that period. A page taken down during a period is **retired**. It is used only to follow where its recommendations went, so they are not counted twice when a site is redesigned.
- **Same page.** A page that moved to a new address or was renamed is treated as the same page.

## 2. What counts as a recommendation

A recommendation is **a single statement about what to write or avoid in a prompt**. It must be readable as "users should (or should not) write, place, remove or change … in the prompt" without further inference.

| Include | Exclude |
|---|---|
| What to say, where to place it, how to structure it | Parameters and API features (temperature, thinking settings, structured output) |
| Statements that a prompt technique works, does not work or is no longer needed | Message roles and channels (system vs. user) |
| Statements that a technique is no longer supported | Tools and the runtime environment |
| Prefilling the start of the answer | Splitting work into several model calls |
| Instructions about when the model should use tools, as written in the prompt | Model choice, fine-tuning, evaluation pipelines, pricing, navigation |

A sentence that mixes a prompt technique with a parameter is split. The prompt part is kept.

## 3. How to divide the text

1. **One recommendation = one technique**: one action on one object, with any condition attached. Different objects become separate recommendations.
2. Reasons, effects and metaphors are not recommendations on their own.
3. Long examples and code blocks are not recommendations. The sentence that introduces them is.
4. The same sentence on several pages of one period forms a **duplicate group** and is counted once.
5. Each recommendation records the models it applies to (`model_scope`), taken from the sentence, then its heading, then the page.

## 4. Following recommendations across versions

1. A recommendation that reappears with identical or nearly identical wording (similarity ≥ .85 after normalization) is **retained**.
2. A recommendation that was rewritten is **revised**. The researcher linked it by hand to its earlier version (`revised_from`).
3. A recommendation that disappears and has no successor is **deleted** (a removal without notice).
4. Recommendations on a model guide that ended because a newer model's guide replaced it are not counted as deleted.
5. A disappearance right after a gap in the archive is marked **uncertain** and not counted as deleted.

## 5. Drafting and checking

A language model drafted the division of each page into recommendations. The researcher checked every unit by hand against these rules, and every quoted recommendation can be found word for word in its source page.

**Reliability.** After two training rounds, two coders independently judged 182 candidate text blocks from three documents not used in training ("include" or "skip"). They reached Krippendorff's α = .81 (Table 1).
