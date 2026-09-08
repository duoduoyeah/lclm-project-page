# LCLM project page — staging draft

Working copy of the public project page, built on `eliahuhorwitz/Academic-project-page-template`
(CC BY-SA 4.0 — attribution kept in the page footer, do not remove it).

Not final. Once the public repo exists, move this whole directory's contents into its `docs/`
folder for GitHub Pages (repo settings → Pages → deploy from `/docs`).

## Structure

- `index.html` — the page. Section order: header/links → TL;DR → **real generation, side by
  side** (moved right under the TL;DR so it's the first thing a reader sees) → hero
  line-interleaving diagram (static, not animated — see TODO below) → three short paragraphs
  (why lines / method / result) → BibTeX. No carousel, no video, no poster — trimmed out of the
  upstream template along with their JS/CSS.
- `static/images/hero-decoding-schedules.png` — rendered at 300dpi from `paper/figures/decoding_schedules.pdf`
  (the paper's Figure 1: block diffusion vs. MTP vs. LCLM decoding schedules).
- `gen-compare.html` + `static/js/gen-compare-data.js` — the "real generation, side by side" section,
  embedded into `index.html` via `<iframe>`. **Real model output**, not schematic: extracted from
  `llm-visual/examples/generation/cdlm_vs_ar_d24r20_daily.json` (matched 881M-parameter, depth-24
  Vanilla AR and LCLM checkpoints). Shows **all 13 matched prompt pairs** in that dump via a
  horizontally scrollable picker, not a curated pair — including prompts where LCLM's own trace
  shows it barely using any parallelism (flagged inline with a "low parallelism on this prompt"
  tag when a prompt ends up with ≤3 total lines). Two of the 13 ("soda vs powder", "used bicycle")
  are the same prompts already published in the paper's qualitative appendix. Self-contained: the
  data was extracted out of `llm-visual` into this folder, so this section has no runtime
  dependency on that repo. Each selected example auto-plays a real step-by-step reveal — AR one
  token/step, LCLM's lines (capped to 8 shown per prompt, for legibility only) filling in together
  per forward pass, with a live tokens/step counter.
  Regenerate the data with `python3 extract_gen_compare_data.py` (reads from `llm-visual/`, writes
  `static/js/gen-compare-data.js`, processes every matched pair in the source file). Edit
  `MAX_LINES_SHOWN` in that script to change how many lines are shown per prompt. The picker leads
  with "soda vs powder" / "used bicycle" (`LEAD_TOPICS` in that script) — the same two prompts
  already published in the paper's qualitative appendix, not a fresh pick — then the other 11
  follow in file order. All 13 stay in the picker; this only reorders display, nothing is hidden.
- `paper.pdf` — the current arXiv-version paper PDF.

## Known placeholders (grep `TODO` in `index.html`)

- arXiv link + BibTeX `arXiv:TODO.TODO` — fill in once the identifier is assigned.
- Author personal-page links — none wired in yet.
- Social preview image (1200x630) — not generated yet.

## Release links already wired

- Code: `https://github.com/duoduoyeah/lclm`
- Model: `https://huggingface.co/duoduoyeah/nanochat-d24-blockmt-v4-r20`
- Project page: `https://duoduoyeah.github.io/lclm-project-page/`

## Not done on purpose (explicitly asked for a concise first pass)

- The hero visual is a **static PNG, not an animated GIF**. It's the paper's Figure 1
  (block diffusion vs. MTP vs. LCLM), which already shows a 5-step decoding progression
  (step=0..4) — a natural candidate to animate later, flagged in an HTML comment above the
  figure but not built yet.
- No separate "Three contributions" / "Scope and limitations" sections — folded into the
  three short paragraphs per instruction. Add them back if the concise version needs more depth.
