"""Reproduce every number, table and figure in the paper from the files in ../data/.

Run from the replication folder:
    python code/reproduce.py

Outputs (written to ../results/):
    shares.csv          share of machine-specific accommodation in each vendor's general guide, by half-year
    figure1.png/.pdf    Figure 1
    table1.md           Table 1 (intercoder reliability)
    table2.md           Table 2 (withdrawals by form and type)
    table3.md           Table 3 (how the guides describe the model as a person)
    numbers.md          every other number cited in the text, labelled by paper section

Category codes used in the data:
    A1 thinking instructions, A2 emphasis and continuation, A3 persona and motivation
    (A1-A3 together = machine-specific accommodation), C general communication, excluded = out of scope.
"""
from __future__ import annotations

import csv
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
DATA, OUT = HERE / "data", HERE / "results"
VENDORS = ["OA", "AN", "GG"]
NAMES = {"OA": "OpenAI", "AN": "Anthropic", "GG": "Google"}
AC = ("A1", "A2", "A3", "C")
PERIODS = [f"{y}H{h}" for y in range(2022, 2027) for h in (1, 2)][1:]   # 2022H2 ... 2026H2
OA_COPY = ("OA", "general", "2024H2")   # OpenAI 2024H2 comes from a repository copy (see Method)
BOOT, BOOT_SEED = 5000, 20261111


def read(name: str) -> list[dict]:
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


UNITS = {u["unit_id"]: u for u in read("units.csv")}
CODES = {c["unit_id"]: c for c in read("codes.csv")}
OCC = read("occurrences.csv")
DOCS = read("documents.csv")
HAS_DATA = {(d["vendor"], d["layer"], d["period"]) for d in DOCS if d["role"] == "current"}
CAT = {k: c["lineage_category"] for k, c in CODES.items()}   # category used in analysis (inherited along revisions)


# ---------- counting what a guide taught in a period ----------

def taught() -> dict[tuple, Counter]:
    """(vendor, layer, period) -> counts of A1/A2/A3/C among 'do' recommendations in current documents.
    A sentence repeated on several pages of the same period is counted once (dup_group)."""
    seen, out = set(), defaultdict(Counter)
    for o in OCC:
        uid = o["unit_id"]
        if o["role"] != "current" or CODES[uid]["stance"] != "do" or CAT[uid] not in AC:
            continue
        key = (o["vendor"], o["layer"], o["period"])
        ident = UNITS[uid]["dup_group"] or uid
        if (key, ident) not in seen:
            seen.add((key, ident))
            out[key][CAT[uid]] += 1
    return out


def n_a(c: Counter) -> int:
    return c["A1"] + c["A2"] + c["A3"]


def share(c: Counter) -> float | None:
    return n_a(c) / (n_a(c) + c["C"]) if n_a(c) + c["C"] else None


# ---------- withdrawals ----------

def withdrawals() -> list[dict]:
    """Explicit retractions ('dont' recommendations) and removals without notice ('deleted')."""
    reason = {w["unit_id"]: w["reason"] for w in read("withdrawals.csv")}
    last = {}
    for o in sorted(OCC, key=lambda o: PERIODS.index(o["period"])):
        last[o["unit_id"]] = (o["period"], o["role"], o["doc_id"])
    out = []
    for uid, u in UNITS.items():
        if CAT[uid] not in AC:
            continue
        base = {"unit_id": uid, "vendor": u["vendor"], "layer": u["layer"], "category": CAT[uid]}
        if CODES[uid]["stance"] == "dont":
            out.append({**base, "method": "retraction", "period": u["first_period"], "reason": reason.get(uid, "")})
        elif u["outcome"] == "deleted":
            p, role, doc = last[uid]
            nxt = PERIODS[min(PERIODS.index(p) + 1, len(PERIODS) - 1)]
            out.append({**base, "method": "removal", "period": p if role == "retired" else nxt, "reason": "", "last_doc": doc})
    return out


# ---------- reliability ----------

def alpha(pairs: list[tuple]) -> float:
    """Krippendorff's alpha, nominal data, two coders, no missing values."""
    o = Counter()
    for a, b in pairs:
        o[(a, b)] += 1
        o[(b, a)] += 1
    n_c = Counter()
    for (a, _), v in o.items():
        n_c[a] += v
    n = sum(n_c.values())
    d_o = sum(v for (a, b), v in o.items() if a != b) / n
    d_e = sum(n_c[a] * n_c[b] for a in n_c for b in n_c if a != b) / (n * (n - 1))
    return 1.0 if d_e == 0 else 1 - d_o / d_e


def boot_ci(pairs: list[tuple]) -> tuple[float, float]:
    """95% percentile interval from bootstrap resamples of units (fixed seed)."""
    rng = random.Random(BOOT_SEED)
    vals = sorted(alpha([pairs[rng.randrange(len(pairs))] for _ in pairs]) for _ in range(BOOT))
    return vals[int(.025 * BOOT)], vals[int(.975 * BOOT) - 1]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


# ---------- outputs ----------

def write_csv(name: str, rows: list[dict]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def shares_and_figure(t: dict) -> None:
    rows = []
    for v in VENDORS:
        for p in PERIODS:
            if (v, "general", p) in HAS_DATA:
                c = t[(v, "general", p)]
                lo, hi = wilson(n_a(c), n_a(c) + c["C"])
                rows.append({"vendor": v, "period": p, "A1": c["A1"], "A2": c["A2"], "A3": c["A3"], "A": n_a(c),
                             "C": c["C"], "A_share": f"{share(c):.3f}", "ci_low": f"{lo:.3f}", "ci_high": f"{hi:.3f}"})
    write_csv("shares.csv", rows)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors, markers = {"OA": "#2a78d6", "AN": "#eb6834", "GG": "#1baf7a"}, {"OA": "o", "AN": "s", "GG": "^"}
    tl = {r["vendor"]: r for r in read("reasoning_models.csv")}
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=200)
    for v in VENDORS:
        pts = [(i, share(t[(v, "general", p)])) for i, p in enumerate(PERIODS) if (v, "general", p) in HAS_DATA]
        segs, cur = [], []
        for i, y in pts:   # break the line at gaps and at the OpenAI repository copy
            if (v, "general", PERIODS[i]) == OA_COPY or (cur and i != cur[-1][0] + 1):
                segs.append(cur) if cur else None
                cur = [] if (v, "general", PERIODS[i]) == OA_COPY else [(i, y)]
                continue
            cur.append((i, y))
        segs.append(cur) if cur else None
        for seg in segs:
            ax.plot([x for x, _ in seg], [y * 100 for _, y in seg], color=colors[v], lw=2, marker=markers[v], ms=6)
        if v == "OA":
            ax.plot([PERIODS.index("2024H2")], [share(t[OA_COPY]) * 100], ls="none", marker="o", ms=7,
                    mfc="white", mec=colors[v], mew=2)
        ax.annotate(NAMES[v], (pts[-1][0], pts[-1][1] * 100), xytext=(8, 0), textcoords="offset points", va="center")
        d = tl[v]["release_date"]
        x = PERIODS.index(f"{d[:4]}H{1 if int(d[5:7]) <= 6 else 2}") + ((int(d[5:7]) - 1) % 6) / 6 - 0.5
        ax.axvline(x, color=colors[v], lw=1, ls=":")
    ax.set_xticks(range(len(PERIODS)), PERIODS)
    ax.set_ylim(0, 42)
    ax.set_ylabel("Machine-specific accommodation (%)")
    ax.grid(axis="y", color="#e5e5e5", lw=0.8)
    ax.legend([plt.Line2D([], [], color=colors[v], marker=markers[v], lw=2) for v in VENDORS]
              + [plt.Line2D([], [], ls="none", marker="o", mfc="white", mec=colors["OA"], mew=2),
                 plt.Line2D([], [], color="#777777", ls=":", lw=1)],
              [NAMES[v] for v in VENDORS] + ["OpenAI 2024H2 (repository copy)", "first reasoning model"],
              frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"figure1.{ext}")
    plt.close(fig)


def table1() -> list[str]:
    rows = []

    def add(name, pairs, unit):
        lo, hi = boot_ci(pairs)
        agree = sum(a == b for a, b in pairs) / len(pairs)
        rows.append(f"| {name} | {unit} | {len(pairs)} | {alpha(pairs):.3f} | [{lo:.3f}, {hi:.3f}] | {agree:.1%} |")
        return alpha(pairs), lo, hi, len(pairs)

    s1 = {r["block_id"]: r["decision"] for r in read("segmentation_coder1.csv")}
    s2 = {r["block_id"]: r["decision"] for r in read("segmentation_coder2.csv")}
    add("Segmentation: recommendation or not", [(s1[k], s2[k]) for k in sorted(s1)], "candidate text blocks")
    c1, c2 = CODES, {r["unit_id"]: r for r in read("codes_coder2.csv")}
    keys = [k for k in sorted(c2) if c1[k]["category"] != "excluded" and c2[k]["category"] != "excluded"]
    add("Type: machine-specific accommodation vs. general communication",
        [(c1[k]["category"][0], c2[k]["category"][0]) for k in keys], "recommendations")
    add("Type: thinking instructions / emphasis and continuation / persona and motivation / general communication",
        [(c1[k]["category"], c2[k]["category"]) for k in keys], "recommendations")
    add("Stance: do vs. avoid", [(c1[k]["stance"], c2[k]["stance"]) for k in keys], "recommendations")
    w1, w2 = {r["unit_id"]: r for r in read("withdrawals.csv")}, {r["unit_id"]: r for r in read("withdrawals_coder2.csv")}
    ks = sorted(set(w1) & set(w2))
    wb = add("Walk-back", [(w1[k]["walk_back"], w2[k]["walk_back"]) for k in ks
                           if w1[k]["walk_back"] and w2[k]["walk_back"]], "revised recommendations")
    rows.pop()   # walk-back is reported in the note only (low reliability, not analyzed)
    add("Reason for withdrawal", [(w1[k]["reason"], w2[k]["reason"]) for k in ks if w1[k]["reason"] and w2[k]["reason"]],
        "withdrawals coded by both coders")
    md = ["**Table 1.** Intercoder reliability (two coders).\n",
          "| Judgment | Units | *n* | Krippendorff's α | 95% CI | Agreement |", "|---|---|---|---|---|---|", *rows, "",
          f"*Note.* Nominal α. 95% CIs are percentile intervals from {BOOT} bootstrap resamples of units (seed {BOOT_SEED}). "
          "Segmentation was tested on three documents not used in coder training. Type and stance were double-coded on a "
          "20% sample of recommendations stratified by vendor, with candidate machine-specific accommodations oversampled; "
          "recommendations either coder judged out of scope are excluded. A third form of withdrawal, walk-back (a rewritten "
          f"recommendation that softens its earlier claim), was double-coded but is not analyzed because reliability was low "
          f"(α = {wb[0]:.2f}, 95% CI [{wb[1]:.2f}, {wb[2]:.2f}], n = {wb[3]})."]
    (OUT / "table1.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return md


def page_context(ws: list[dict]) -> dict[str, str]:
    """For removals: was the page still there ('page_kept') or taken down or merged ('page_removed')?"""
    doc = {d["doc_id"]: d for d in DOCS}
    current = {(d["series_id"], d["period"]) for d in DOCS if d["role"] == "current"}
    return {w["unit_id"]: "page_kept" if (doc[w["last_doc"]]["series_id"], w["period"]) in current else "page_removed"
            for w in ws if w["method"] == "removal"}


def rates_ever_taught() -> dict[str, tuple[int, int]]:
    """Among 'do' recommendations ever taught in a current document: how many were later removed without notice."""
    ever = defaultdict(set)
    for o in OCC:
        uid = o["unit_id"]
        if o["role"] == "current" and CODES[uid]["stance"] == "do" and CAT[uid] in AC:
            ever[CAT[uid][0]].add(uid)
    return {ac: (sum(UNITS[k]["outcome"] == "deleted" for k in us), len(us)) for ac, us in ever.items()}


def table2(ws: list[dict]) -> dict:
    ctx = page_context(ws)
    groups = [("Explicit retraction", lambda w: w["method"] == "retraction"),
              ("Removal without notice: page taken down or merged", lambda w: ctx.get(w["unit_id"]) == "page_removed"),
              ("Removal without notice: page continued", lambda w: ctx.get(w["unit_id"]) == "page_kept"),
              ("Total", lambda w: True)]
    rows = []
    for name, f in groups:
        a = sum(1 for w in ws if f(w) and w["category"][0] == "A")
        c = sum(1 for w in ws if f(w) and w["category"] == "C")
        rows.append((name, a, c))
    pct = lambda k, n: f"{k} ({k / n:.0%})"
    ex_a, ex_c = rows[0][1] / rows[-1][1], rows[0][2] / rows[-1][2]
    r = rates_ever_taught()
    walk_backs = sum(w["walk_back"] == "yes" and CODES[w["unit_id"]]["stance"] == "do" and CAT[w["unit_id"]] in AC
                     for w in read("withdrawals.csv"))
    md = ["**Table 2.** Withdrawals of recommendations, by form and type.\n",
          "| Form of withdrawal | *n* | Machine-specific accommodation | General communication |", "|---|---|---|---|"]
    md += [f"| {n} | {a + c} | {pct(a, a + c)} | {pct(c, a + c)} |" for n, a, c in rows]
    md += ["", "*Note.* All three vendors, general and model guides. \"Page taken down or merged\": the page carrying the "
               "recommendation had no current version in the period of removal. Of recommendations that a current guide "
               "presented as advice to follow, "
               f"{r['A'][0] / r['A'][1]:.1%} of machine-specific accommodation and {r['C'][0] / r['C'][1]:.1%} of general "
               f"communication were later removed without notice. Of withdrawn machine-specific accommodation, {ex_a:.0%} was "
               f"explicitly retracted, compared with {ex_c:.0%} of withdrawn general communication. Walk-backs ({walk_backs} by "
               "the first coder) are excluded because of low reliability."]
    (OUT / "table2.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return {"rows": rows, "ex_a": ex_a, "ex_c": ex_c, "rates": r}


NOT_METAPHOR = {   # keyword hits that are not descriptions of the model (decided by the researcher)
    "With that rule, the model held back roughly half of its routine requests to colleagues and other teams.",
    "Show your prompt to a colleague, ideally someone who has minimal context on the task, and ask them to follow the instructions.",
    "Golden rule:** Show your prompt to a colleague with minimal context on the task and ask them to follow it.",
    "Key test:** Show your prompt to a colleague with minimal context on the task and ask them to follow it.",
}


def table3() -> None:
    spans: dict[tuple, list[str]] = {}
    for r in read("colleague_sentences.csv"):
        if r["sentence"] not in NOT_METAPHOR:
            spans.setdefault((r["vendor"], r["sentence"].replace("**", "")), []).append(r["period"])
    out = []
    for (v, s), ps in spans.items():
        ps = sorted(set(ps), key=PERIODS.index)
        out.append((VENDORS.index(v), PERIODS.index(ps[0]), PERIODS.index(ps[-1]), NAMES[v], ps[0], ps[-1], s))
    out.sort(key=lambda o: o[:3])   # stable: ties keep the order in which sentences first appear
    md = ["**Table 3.** How the guides describe the model as a person.\n", "| Vendor | Period | Wording in the guide |", "|---|---|---|"]
    md += [f"| {n} | {a}{'–' + b if b != a else ''} | \"{s}\" |" for *_, n, a, b, s in out]
    md += [f"| {NAMES[v]} | — | No such description found |" for v in VENDORS if NAMES[v] not in {o[3] for o in out}]
    md += ["", "*Note.* Sentences containing colleague, coworker, employee, new hire, intern, or teammate, extracted by script from all "
               "sampled documents (current and retired versions), excluding example dialogues and code blocks (text addressed to "
               "the model). Sentences in which a colleague is a real person or a test reader of the prompt are omitted. Periods are "
               "half-years in which the sentence appears."]
    (OUT / "table3.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def model_specific_share() -> dict[tuple, float]:
    """Share of 'do' recommendations in a general guide that apply only to named models."""
    seen, c = set(), defaultdict(Counter)
    for o in OCC:
        uid = o["unit_id"]
        if o["role"] != "current" or o["layer"] != "general" or CODES[uid]["stance"] != "do" or CAT[uid] not in AC:
            continue
        key = (o["vendor"], o["period"], UNITS[uid]["dup_group"] or uid)
        if key not in seen:
            seen.add(key)
            c[(o["vendor"], o["period"])]["specific" if UNITS[uid]["model_scope"] else "general"] += 1
    return {k: v["specific"] / (v["specific"] + v["general"]) for k, v in c.items() if v["specific"] + v["general"]}


def numbers(t: dict, ws: list[dict], t2: dict) -> None:
    L = ["# Numbers cited in the text\n", "Generated by code/reproduce.py. Section labels follow the paper.\n"]
    cur = [d for d in DOCS if d["role"] == "current"]
    L += ["## Method (corpus)\n",
          f"- Documents: {len(DOCS)} ({len(cur)} current at the end of a period, {len(DOCS) - len(cur)} taken down partway through one)",
          f"- Units: {len(UNITS)}, of which {sum(c['category'] == 'excluded' for c in CODES.values())} were coded out of scope, "
          f"leaving {sum(c['category'] != 'excluded' for c in CODES.values())} recommendations for analysis", ""]

    L += ["## 4.1 How the balance shifted\n", "Share of machine-specific accommodation in each general guide (peak and latest):\n"]
    for v in VENDORS:
        sh = [(p, share(t[(v, "general", p)])) for p in PERIODS if (v, "general", p) in HAS_DATA]
        peak = max(sh, key=lambda x: x[1])
        L.append(f"- {NAMES[v]}: peak {peak[1]:.0%} ({peak[0]}), latest {sh[-1][1]:.0%} ({sh[-1][0]})")
    g = lambda v, p: t[(v, "general", p)]
    L += ["", "Counts behind the different paths (general guides):\n",
          f"- OpenAI 2024H2 -> 2026H2: machine-specific {n_a(g('OA', '2024H2'))} -> {n_a(g('OA', '2026H2'))}, "
          f"general communication {g('OA', '2024H2')['C']} -> {g('OA', '2026H2')['C']}",
          f"- Anthropic 2025H2 -> 2026H2: machine-specific {n_a(g('AN', '2025H2'))} -> {n_a(g('AN', '2026H2'))}, "
          f"general communication {g('AN', '2025H2')['C']} -> {g('AN', '2026H2')['C']}",
          f"- Google 2023H2 -> 2026H2: machine-specific {n_a(g('GG', '2023H2'))} -> {n_a(g('GG', '2026H2'))}; "
          f"general communication 2025H1 -> 2025H2: {g('GG', '2025H1')['C']} -> {g('GG', '2025H2')['C']}",
          f"- Google withdrew {sum(1 for w in ws if w['vendor'] == 'GG' and w['layer'] == 'general' and w['category'][0] == 'A')} "
          "machine-specific recommendations from its general guide", ""]
    L += ["Forms in the general guides, 2026H2 (thinking / emphasis / persona):\n"]
    L += [f"- {NAMES[v]}: {g(v, '2026H2')['A1']} / {g(v, '2026H2')['A2']} / {g(v, '2026H2')['A3']}" for v in VENDORS]
    L.append(f"- Google emphasis and continuation: {g('GG', '2025H1')['A2']} before 2026, {g('GG', '2026H2')['A2']} in 2026H2")
    a1 = [w for w in ws if w["method"] == "retraction" and w["category"] == "A1"]
    a1_an = sum(1 for w in a1 if w["vendor"] == "AN" and w["layer"] == "model" and w["period"] == "2026H2")
    L += [f"- Retractions of thinking instructions: {a1_an} of {len(a1)} in Anthropic's 2026H2 model guides", ""]
    tl = {r["vendor"]: r for r in read("reasoning_models.csv")}
    L += ["Shares before and after each vendor's first reasoning model (general guides; a period counts as 'after' "
          "if its latest snapshot is on or after the release date):\n"]
    snap = defaultdict(str)
    for d in cur:
        if d["layer"] == "general":
            snap[(d["vendor"], d["period"])] = max(snap[(d["vendor"], d["period"])], d["snapshot_time"][:8])
    for v in VENDORS:
        rel = tl[v]["release_date"].replace("-", "")
        cells = [f"{p} {share(g(v, p)):.0%} ({'after' if snap[(v, p)] >= rel else 'before'})"
                 for p in PERIODS if (v, "general", p) in HAS_DATA]
        L.append(f"- {NAMES[v]} ({tl[v]['model']}, {tl[v]['release_date']}): " + ", ".join(cells))
    L.append("")

    wa = [w for w in ws if w["category"][0] == "A"]
    L += ["## 4.2 How machine-specific accommodation was withdrawn\n",
          f"- Withdrawals of machine-specific accommodation: {len(wa)} "
          f"({sum(w['method'] == 'retraction' for w in wa)} explicit retractions, {sum(w['method'] == 'removal' for w in wa)} removals without notice)",
          f"- Share explicitly retracted: machine-specific {t2['ex_a']:.0%}, general communication {t2['ex_c']:.0%}",
          "- Retractions by form: " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(w['category'] for w in wa if w['method'] == 'retraction').items())),
          "- Removals by form: " + ", ".join(f"{k} {n}" for k, n in sorted(Counter(w['category'] for w in wa if w['method'] == 'removal').items())),
          "- Withdrawals by vendor: " + ", ".join(f"{NAMES[v]} {sum(w['vendor'] == v for w in wa)}" for v in VENDORS),
          "- Reasons given in explicit retractions: " + ", ".join(
              f"{r or 'no reason'} {n}" for r, n in Counter(w["reason"] for w in wa if w["method"] == "retraction").most_common()),
          ""]
    ms = model_specific_share()
    L += ["## 4.3 How the guides present the model\n",
          "- Recommendations in the general guide that apply only to named models, 2026H2: "
          + ", ".join(f"{NAMES[v]} {ms[(v, '2026H2')]:.0%}" for v in VENDORS),
          "- Highest share before 2025: " + ", ".join(
              f"{NAMES[v]} {max([ms[(v, p)] for p in PERIODS[:5] if (v, p) in ms] or [0]):.0%}" for v in VENDORS), ""]
    r = t2["rates"]
    L += ["## Table 2 note\n",
          f"- Later removed without notice: machine-specific {r['A'][0]}/{r['A'][1]} = {r['A'][0] / r['A'][1]:.1%}, "
          f"general communication {r['C'][0]}/{r['C'][1]} = {r['C'][0] / r['C'][1]:.1%}"]
    (OUT / "numbers.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    t = taught()
    ws = withdrawals()
    shares_and_figure(t)
    table1()
    t2 = table2(ws)
    table3()
    numbers(t, ws, t2)
    print("Wrote results/: shares.csv, figure1.png/.pdf, table1.md, table2.md, table3.md, numbers.md")


if __name__ == "__main__":
    main()
