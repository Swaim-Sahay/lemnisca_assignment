Q1 — Routing Logic

Rules: Short query + single entity + "what/who/when" = simple. Anything with "compare", "why", "how", multi-part structure, or over ~20 tokens = complex.
Why here: Cost. Simple queries don't need deep retrieval or a big model. The line is drawn where one-hop lookup stops being enough.Misclassification: "What is GDPR?" routes simple. User actually wanted GDPR vs CCPA comparison. Router saw "What is" and short length, missed the intent. Output was correct but incomplete — worst kind of failure because it's invisible.Fix without LLM: Train a logistic regression on labeled queries. Features: token count, entity count, presence of comparison/negation bigrams, question word type. Fast, cheap, meaningfully better than keyword matching.

Q2 — Retrieval Failures

Query: "What were the board's concerns about the merger in Q3?
What the doc actually said: "Directors raised reservations about the proposed acquisition."What was retrieved: Wrong chunk, or nothing. "Concerns" vs "reservations", "board" vs "directors", "merger" vs "acquisition" — all close but not close enough in embedding space. Chunk boundary probably cut the section header off too, losing context.
Fix: Hybrid retrieval (BM25 + dense), keep section headers in every chunk, try HyDE if vocabulary mismatch is systematic.

Q3 — Cost and Scale

Assumptions: 60% simple (Llama 8B), 40% complex (Llama 70B). Context: 800 tokens simple, 2500 complex. Query: 50 tokens. Output: 300 simple, 600 complex.
Simple (3,000/day): 3,000 × 850 input + 300 output = ~3.45M tokens on 8B
Complex (2,000/day): 2,000 × 2,550 input + 600 output = ~6.3M tokens on 70B
Biggest cost driver: Complex path. 40% of queries, ~80% of cost because 70B costs 4-8x more per token.
Highest ROI change: Reranker on complex queries. Cut context from 2,500 → 1,500 tokens. Removes 2M expensive tokens/day, and answer quality actually improves.
What to avoid: Query-answer caching. Cache hit rate on non-FAQ workloads is under 15%, you get staleness bugs when corpus updates, and the engineering cost isn't justified until you've confirmed repetition in real logs.

Q4 — What Is Broken

The flaw: No faithfulness check. The model can ignore retrieved chunks entirely and answer from memory — confidently, fluently, wrongly. There's no mechanism that catches this.
Why it shipped: It's invisible in demos. Happy path looks perfect. Failures are rare enough in light testing that nobody panics.
The fix: Post-generation grounding check. Run a lightweight NLI model (DeBERTa-class) that checks whether the answer is actually entailed by the retrieved chunks. Anything that fails gets flagged or regenerated. Changes the failure mode from silent and confident to caught and handled.

---

## AI Usage

The following are the exact verbatim prompts provided by the user during this session:

**Prompt Set 1 (Backend Initialization):**
```text
gave text from all 3 layers from docs and told you are a senior python developer and you have to build a rag chatbot according to the text given to you and you have to build a rag chatbot with the following features.
```

**Prompt Set 2 (Documentation Setup):**
```text
gave all ss of all docs process and told to add all pdf files and readme too which i have provided to you.
```

**Prompt Set 3 (Project Structure):**
```text
for rest of folders gave ss of folder structure from docs and asked to create a folder structure like this.
```

**Prompt 4:**
```text
Written Questions
Answer these in a file called written_answers.md. Aim for 150-250 words per question.and also remove all fluff and unnecessary details.

Q1 — Routing Logic
Share the exact rules your router uses to classify a query as simple or complex. Then answer:
Why did you draw the boundary here?
Give one example of a query your router misclassified. What happened and why?
If you had to improve the router without using an LLM, what would you change?

Q2 — Retrieval Failures
Describe a case where your RAG pipeline retrieved the wrong chunk — or nothing at all.
What was the query?
What did your system retrieve (or fail to retrieve)?
Why did the retrieval fail?
What would fix it?

If you did not observe a real failure during testing, construct a realistic one and reason through it.

Q3 — Cost and Scale
Imagine this system handles 5,000 queries per day. Using Groq's free-tier limits as a proxy for proportional costs:
Estimate daily token usage broken down by model — show your working
Where is the biggest cost driver?
What is the single highest-ROI change to reduce cost without hurting quality?
What optimisation would you avoid, and why?

Q4 — What Is Broken
What is the most significant flaw in the system you built? Not a polish issue — a genuine limitation that would cause real problems if this were deployed.
What is it?
Why did you ship with it anyway?
If you had more time, what single change would fix it most directly?
```

**Prompt 2:**
```text
Your README must include:
How to run the project locally — exact setup and start commands
Which Groq models you used and any environment config
Which bonus challenges you attempted, if any
Any known issues or limitations


for readme.md file i gave all points that are mentioned in docs that it should include.in prompt wrote that readme files must include all points that are mentioned in docs.