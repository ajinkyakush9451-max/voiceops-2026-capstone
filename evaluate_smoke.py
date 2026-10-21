"""Small smoke test; not a substitute for the official practice evaluation."""
from src.agent import SupportAgent, load_chunks
def main():
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} policy sections from local kb/")
    agent = SupportAgent()
    tests = [
        "What is the return window for electronics?",
        "How long do UPI refunds take after initiation?",
        "How much does ZentroMart Plus cost?",
    ]
    for q in tests:
        print("\nQ:", q)
        print("A:", agent.respond(q))
    print("\nNOTE: This smoke test does not calculate official accuracy scores.")
if __name__ == "__main__":
    main()
