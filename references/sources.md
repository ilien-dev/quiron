# Sources

Every study and dataset behind a number in this skill.

- Reinhart, Brown et al. (2025). *Do LLMs write like humans? Variation in grammatical and
  rhetorical styles.* PNAS 122. HAP-E corpus, six registers; participial clauses 5.3x,
  nominalizations 2.1x, agentless passive about 0.5x, per-word ratios.
- Juzek (2026). *AI-Associated Lexical Shifts Across 34 Languages*, arXiv:2605.25358, and
  the LexA index (CC0 data, github.com/fsu-nlp/lexa-index): word ratios for GPT-4.1-mini
  news and GPT-3.5, Claude 3 Haiku, Gemini 3 Flash and GPT-5.2 science continuations.
- Kobak, González-Márquez, Horvát & Lause (2025). *Delving into LLM-assisted writing in
  biomedical publications through excess vocabulary.* Science Advances 11:eadt3813.
  15.1M PubMed abstracts; delves r=28, underscores r=13.8, showcasing r=10.7; of the
  2024 excess style words, 66% verbs and 14% adjectives.
- Liang et al. (2024). *Monitoring AI-Modified Content at Scale.* ICML 2024,
  arXiv:2403.07183. Peer reviews; commendable 9.8x, intricate 11.2x, meticulous 34.7x.
- Juzek & Ward (2025). *Why Does ChatGPT "Delve" So Much?* COLING 2025. The overuse is
  consistent with a role for learning from human feedback; the human study is
  exploratory.
- Geng & Trotta (2024, 2025). *Is ChatGPT Transforming Academics' Writing Style?* and
  *Human-LLM Coevolution*, ACL Findings 2025.
- Russell, Karpinska & Iyyer (2025). *People who frequently use ChatGPT for writing
  tasks are accurate and robust detectors of AI-generated text.* ACL 2025,
  arXiv:2501.15654.
- Chakrabarty et al. (2025). *Can AI writing be salvaged?* CHI 2025, arXiv:2409.14509.
  LAMP corpus: 1,057 paragraphs, 8,035 edits by 18 professional writers.
- Paech et al. (2025). *Antislop*, arXiv:2510.15061, and the slop-score leaderboard
  (github.com/sam-paech/slop-score): over-used words, phrases and contrast patterns
  across 67 models against a human baseline.
- Shaib et al. (2025). *Measuring AI "SLOP" in Text*, arXiv:2509.19163.
- The Economist (30 July 2026). *How to spot AI writing.* 1.2M words from four chatbots
  against journalists.
- Freeburg (2026), arXiv:2603.27006, em-dash rates by model and version.
- Cheng et al. (2025), PMC12752165, blinded raters' accuracy.
- Chakrabarty et al. (2026). arXiv:2510.13939 v4. Expert readers against prompted and
  author-fine-tuned model prose; cliché density and detector rates.
- Sun et al. (2025). *Idiosyncrasies in Large Language Models.* ICML 2025,
  arXiv:2502.12150. Model identification from word choice and from markdown layout.
- TURING (LREC 2026), 500 French texts and 214 readers: readers 59.3% accurate, and
  texts they called "monotonous" were labelled AI 80% of the time against 30% for
  "varied".
- *Prompt to Press* (IUI 2026), 150 readers, human articles edited by AI.
- Alonso Simón et al. (2025), *RAEL*: Spanish human and GPT-3.5/4 texts in three genres.
- TextPulse Research (2026), six self-published working papers with Zenodo DOIs, not
  peer reviewed, from a company that sells a tool for rewriting AI text. Four use one paired corpus of
  60,786 human academic texts and AI rewrites of them (the vocabulary fingerprint, the
  sentence-length burstiness study, the 49-feature stylometric fingerprint, the
  human-vs-AI classification study). *Do AI Models Speak Human?* uses ten PMC passages
  and *Modelometry* uses LMArena chat.
- Herbold et al. (2023) on structural uniformity in ChatGPT essays.
- Fan, Lewis & Dauphin (2018). *Hierarchical Neural Story Generation.* ACL 2018. The
  WritingPrompts corpus the fiction bands are built from.
- Wikipedia WikiProject AI Cleanup, *Signs of AI writing* (September 2026 version),
  including its era word lists, its historical indicators and its signs of human writing.
- This skill's own run: `scripts/build-corpus.sh` for the human corpus, and
  `scripts/evaluate.py` for every rate marked *measured* above.
