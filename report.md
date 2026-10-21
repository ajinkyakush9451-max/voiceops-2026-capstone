# VoiceOps 2026 Capstone Report
## ZentroMart AI Customer Support Agent

### 1. Problem and objective
ZentroMart is a fictional Indian online retailer whose support team repeatedly handles delivery, cancellation, returns, refunds, warranty, and membership questions. The objective is to build a conversational assistant that answers from company documents, uses mock order tools safely, escalates unresolved cases, and supports spoken interaction through Gnani speech models.

### 2. System design
The pipeline is customer audio → Gnani speech-to-text (STT) → conversational agent → policy retrieval + LLM + order/ticket tools → Gnani text-to-speech (TTS) → spoken response. The implementation splits Markdown knowledge-base files at section IDs and retains document title, status, and effective date. Lexical retrieval ranks query/section token overlap, prefers current policy documents, and penalizes superseded content. Retrieved excerpts are supplied to an LLM with explicit grounding instructions. If an LLM API key is not configured, the text agent returns a matching excerpt as a transparent fallback rather than inventing a policy.

### 3. Conversation and safety
The agent introduces itself as an AI assistant, retains recent conversational turns, asks for an order ID when needed, and requires either the registered phone's last four digits or delivery pincode before order details are shown. It does not report a ticket handover unless the ticket tool returns `created=True`. The supplied tools are synthetic educational tools and are not production-grade authentication. The reference date and business-day rules follow the capstone brief.

### 4. Evaluation
The official practice pack contains 52 single-question cases and 23 multi-turn conversations (96 customer turns). The included validation script checks dataset row counts, keys, foreign-key joins, order totals, policy section IDs, practice evidence, and order-verification gates. **Evaluation scores are pending execution against the complete official dataset.** No Step 1/Step 2 accuracy numbers are reported here because they have not been measured in this environment. Before submission, run the validator and evaluation harness, record actual scores, inspect failures, and add a short error analysis.

### 5. Limitations and next steps
The lexical retriever is a baseline and may miss semantic matches. Only five policy files were available in the supplied uploads, whereas the brief specifies 21 knowledge-base documents and nine CSVs. The official dataset ZIP must be extracted before the full validator and practice suite can run. The Gnani SDK calls must be tested with an individual Gnani account and API key. Next steps are to add a measured prompt-only baseline, evaluate RAG retrieval and answer correctness, test all conversations including verification retries and escalation, and record a two-minute spoken demo.

### 6. Deliverables
The repository includes Python agent code, optional Gnani audio batch wrapper, provided mock tools and validator, supplied policy/practice files, environment-variable template, and setup instructions. Public GitHub and demo URLs should be added after they are created and access-tested.
