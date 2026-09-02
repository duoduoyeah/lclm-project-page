#!/usr/bin/env python3
"""Regenerate static/js/gen-compare-data.js for the project page's
"real generation, side by side" section.

Source of truth: llm-visual/examples/generation/cdlm_vs_ar_d24r20_daily.json
(matched 881M-parameter, depth-24 Vanilla AR vs. LCLM checkpoints).

Processes EVERY matched prompt pair in that file, not a curated subset --
this is meant to be an honest trace viewer (the reader picks which prompt to
look at), so we don't get to filter out ones where LCLM does worse. Two of
these prompts are already published in the paper's qualitative appendix
(baking soda vs. powder, used bicycle); the rest are additional real traces
from the same dump.

Reconstructs LCLM's parallel lines from the flat `rope` index (line id =
rope // 256, per the model's rope_stride) and caps the displayed line count
for legibility only -- not for cherry-picking content. AR and LCLM are both
capped at LCLM's own natural step count for that prompt, so nothing is cut
short artificially.

Run from anywhere; writes next to this script.
"""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent.parent / "llm-visual" / "examples" / "generation" / "cdlm_vs_ar_d24r20_daily.json"
OUT_JS = HERE / "static" / "js" / "gen-compare-data.js"

MAX_LINES_SHOWN = 8


def gen_only(seqs, name):
    return [t for t in seqs[name]["tokens"] if t["step"] > 0]


def prompt_text(seqs, name):
    return "".join(t["char"] for t in seqs[name]["tokens"] if t["step"] == 0).replace("<|bos|>", "").strip()


def main():
    data = json.loads(SOURCE.read_text())
    seqs = {s["name"]: s for s in data["sequences"]}

    # Pair every "AR ..." sequence with its matching "CDLM ..." sequence by
    # the shared topic suffix after the "· " separator -- process ALL pairs
    # found in the file, in the order they appear.
    ar_by_topic = {}
    lc_by_topic = {}
    topic_order = []
    for name, seq in seqs.items():
        model, _, topic = name.partition(" · ")
        topic = topic.strip()
        if seq["model"] == "ar":
            ar_by_topic[topic] = name
            if topic not in topic_order:
                topic_order.append(topic)
        elif seq["model"] == "lclm":
            lc_by_topic[topic] = name

    # All 13 stay available -- this only sets *display order*, so the first
    # thing a reader sees is one of the two prompts the paper's own
    # qualitative appendix already vetted, not an arbitrary file-order pick.
    # Nothing is hidden or dropped; everything else still follows below.
    LEAD_TOPICS = ["soda vs powder", "used bicycle"]
    topic_order = [t for t in LEAD_TOPICS if t in topic_order] + \
                  [t for t in topic_order if t not in LEAD_TOPICS]

    examples = []
    for topic in topic_order:
        if topic not in lc_by_topic:
            continue  # no matched LCLM trace for this AR sequence -- skip, don't fabricate
        ar_name, lc_name = ar_by_topic[topic], lc_by_topic[topic]

        ar_gen = gen_only(seqs, ar_name)
        lc_gen = gen_only(seqs, lc_name)
        cap_step = max(t["step"] for t in lc_gen)  # LCLM's own natural end

        lines = collections.defaultdict(list)
        for t in lc_gen:
            lines[t["rope"] // 256].append(t)
        activation_order = sorted(lines.keys(), key=lambda li: min(t["step"] for t in lines[li]))
        keep = set(activation_order[:MAX_LINES_SHOWN])

        ar_cap = [t for t in ar_gen if t["step"] <= cap_step]

        examples.append({
            "key": topic.lower().replace("/", "-").replace(" ", "-"),
            "title": topic[:1].upper() + topic[1:],
            "prompt": prompt_text(seqs, ar_name),
            "maxStep": cap_step,
            "ar": [t["char"] for t in ar_cap],
            "totalLines": len(lines),
            "shownLines": len(keep),
            "lines": [
                {
                    "id": li,
                    "tokens": [{"step": t["step"], "char": t["char"]} for t in sorted(lines[li], key=lambda x: x["step"])],
                }
                for li in sorted(keep)
            ],
        })

    OUT_JS.write_text("const GEN_COMPARE_DATA = " + json.dumps({"examples": examples}) + ";\n")
    for ex in examples:
        print(f"{ex['key']}: ar_len={len(ex['ar'])} total_lines={ex['totalLines']} "
              f"shown={ex['shownLines']} maxStep={ex['maxStep']}")
    print(f"wrote {len(examples)} examples to {OUT_JS}")


if __name__ == "__main__":
    main()
