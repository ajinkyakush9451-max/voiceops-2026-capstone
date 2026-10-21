"""ZentroMart grounded support agent for VoiceOps 2026.

Uses a lightweight lexical retriever and an OpenAI-compatible chat API when configured.
No policy answer is hardcoded; responses are grounded in retrieved knowledge-base chunks.
"""
from __future__ import annotations
import csv, os, re, json
from pathlib import Path
from dataclasses import dataclass
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KB_DIR = ROOT / "kb"
DATA_DIR = ROOT / "data"

@dataclass
class Chunk:
    section_id: str
    title: str
    text: str
    source: str
    status: str
    effective_from: str

def _metadata(text: str, key: str, default: str = "") -> str:
    m = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", text)
    return m.group(1).strip() if m else default

def load_chunks(kb_dir: Path = KB_DIR) -> list[Chunk]:
    chunks = []
    if not kb_dir.exists():
        return chunks
    for path in sorted(kb_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        title = _metadata(raw, "title", path.stem)
        status = _metadata(raw, "status", "unknown").lower()
        effective = _metadata(raw, "effective_from", "")
        # Split at section headings while preserving their IDs.
        parts = re.split(r"(?m)^##\s*\[([^\]]+)\]\s*", raw)
        for i in range(1, len(parts), 2):
            sid, body = parts[i], parts[i+1]
            body = body.strip()
            if body:
                chunks.append(Chunk(sid, title, body, path.name, status, effective))
    return chunks

def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9₹]+", text.lower()))

def retrieve(query: str, chunks: list[Chunk], k: int = 5) -> list[Chunk]:
    q = _tokens(query)
    scored = []
    for c in chunks:
        text = f"{c.title} {c.section_id} {c.text}"
        terms = _tokens(text)
        overlap = len(q & terms)
        if overlap == 0:
            continue
        # Prefer current documents; superseded policy is penalized heavily.
        score = overlap / max(1, len(q) ** 0.5)
        if c.status == "current":
            score *= 1.25
        elif c.status == "superseded":
            score *= 0.15
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for score, c in scored[:k] if score > 0]

SYSTEM_PROMPT = """You are ZentroMart's customer-support assistant. Begin the first response by clearly
saying you are an AI assistant. Answer only from the supplied retrieved company-document excerpts
and verified tool results. Do not invent policy, amounts, dates, delivery estimates, or actions.
If evidence is insufficient, say you cannot confirm from the available policy and offer a human
handover when appropriate. Keep replies concise and natural for speech. Preserve conversation
context and ask one clear question when a required detail is missing.
For order details, never disclose anything until lookup_order confirms verified=True. Ask for the
order ID, then ask for either the registered phone's last four digits or delivery pincode. Permit
at most one verification retry. Never reveal expected verification values. For escalation, call
create_ticket with a useful summary and claim handover only if created=True.
The reference date for the supplied dataset is 20 October 2026. Business days are Monday-Saturday
excluding holidays.csv; return windows use calendar days. Use current policies over superseded
policies. Do not treat support logs as policy authority.
"""

class SupportAgent:
    def __init__(self):
        self.chunks = load_chunks()
        self.history: list[dict[str,str]] = []
        self.order_id: str | None = None
        self.verification_attempts = 0
        self.verified_order: dict[str, Any] | None = None
        self.intro_pending = True
        self._tools_available = False
        try:
            from tools import lookup_order, create_ticket
            self.lookup_order, self.create_ticket = lookup_order, create_ticket
            self._tools_available = True
        except Exception:
            self.lookup_order = self.create_ticket = None

    def _llm(self, user_text: str, evidence: list[Chunk]) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._fallback(user_text, evidence)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL") or None)
            model = os.getenv("LLM_MODEL", "gpt-4o-mini")
            excerpt = "\n\n".join(
                f"[{c.section_id}] {c.title} | status={c.status} | effective_from={c.effective_from}\n{c.text}"
                for c in evidence
            )
            messages = [{"role":"system","content":SYSTEM_PROMPT + "\n\nRetrieved evidence:\n" + (excerpt or "[NO RELEVANT EVIDENCE]")}]
            messages += self.history[-8:]
            messages.append({"role":"user","content":user_text})
            result = client.chat.completions.create(model=model, messages=messages, temperature=0.1)
            answer = result.choices[0].message.content or ""
            self.history.extend([{"role":"user","content":user_text},{"role":"assistant","content":answer}])
            self.history = self.history[-12:]
            return answer
        except Exception as exc:
            return "I couldn't reach the language model service just now. Please try again, or I can help create a support ticket. (Technical detail: " + type(exc).__name__ + ")"

    def _fallback(self, user_text: str, evidence: list[Chunk]) -> str:
        if not evidence:
            return "I can't confirm that from the company documents available to me. Would you like me to arrange a human support follow-up?"
        best = evidence[0]
        # Safe baseline: return the matching policy excerpt rather than fabricate a synthesized answer.
        excerpt = re.sub(r"\n{2,}", "\n", best.text).strip()
        return f"Based on {best.title} ({best.section_id}): {excerpt[:900]}"

    def respond(self, user_text: str) -> str:
        msg = user_text.strip()
        if not msg:
            return "Sorry, I didn't catch that. Could you say it again?"
        lower = msg.lower()

        # Basic order intent and verification workflow.
        order_match = re.search(r"\b(?:order\s*(?:id|number|#)?\s*[:#-]?\s*)(\d{5,})\b", msg, re.I)
        if order_match:
            self.order_id = order_match.group(1)
        asks_order = any(x in lower for x in ("my order", "order status", "where is my order", "track my order", "cancel my order", "my delivery", "my refund"))
        proof_match = re.search(r"\b(\d{4}|\d{6})\b", msg)
        if asks_order and not self.order_id and not order_match:
            return "I'm ZentroMart's AI support assistant. Could you share your order ID so I can check the right order?"
        if self.order_id and asks_order and not self.verified_order and self._tools_available:
            if proof_match:
                result = self.lookup_order(self.order_id, verification_value=proof_match.group(1))
                if result.get("verified") is True:
                    self.verified_order = result
                    self.verification_attempts = 0
                    return "I've verified the order. " + self._summarize_order(result)
                self.verification_attempts += 1
                if self.verification_attempts >= 2:
                    return "I couldn't verify those details. To protect your information, I can't disclose the order. Please contact a human support agent."
                return "That verification didn't match. Please try once more with the registered phone's last four digits or the delivery pincode."
            return "For privacy, I need to verify the order first. Please provide either the registered phone's last four digits or the delivery pincode."
        if any(x in lower for x in ("human", "agent", "compensation", "complaint", "escalate")):
            return self._handover(msg)
        evidence = retrieve(msg, self.chunks)
        answer = self._llm(msg, evidence)
        if self.intro_pending:
            self.intro_pending = False
            if "AI" not in answer and "ai" not in answer.lower():
                answer = "Hello, I'm ZentroMart's AI support assistant. " + answer
        return answer

    def _summarize_order(self, order: dict[str, Any]) -> str:
        fields = []
        for key, label in (("status","status"),("promised_date","promised delivery date"),("payment","payment method")):
            if order.get(key) not in (None, ""):
                fields.append(f"{label}: {order[key]}")
        return "; ".join(fields) if fields else "The verified order record contains no additional summary fields."

    def _handover(self, msg: str) -> str:
        if not self._tools_available:
            return "This needs human support, but the ticket tool is not available in this setup."
        summary = f"Customer request: {msg}. Relevant policy and order checks should be reviewed by a human agent."
        result = self.create_ticket(summary, order_id=self.order_id, reason="human review requested", intent="support_escalation")
        if result.get("created") is True:
            return f"I've created a support ticket, reference {result.get('ticket_id')}. A human support agent can review this request."
        return "I couldn't create the ticket successfully, so I can't confirm a handover. Please try again or contact support directly."

def main():
    agent = SupportAgent()
    print("ZentroMart support agent. Type 'quit' to exit.")
    while True:
        try:
            msg = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            break
        if msg.strip().lower() in {"quit","exit"}:
            break
        print("Agent:", agent.respond(msg))

if __name__ == "__main__":
    main()
