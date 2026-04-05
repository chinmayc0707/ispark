class QueryEnricher:
    def __init__(self):
        pass

    def enrich_query(self, recent_turns, current_query):
        # In a real system, this would call an LLM.
        # Here we mock the behavior for the specific example.
        context_str = " | ".join([f"{t['role']}: {t['content']}" for t in recent_turns])

        # Example logic for resolving pronoun
        if "what did they report" in current_query.lower() and "Apple" in context_str:
            return "What did Apple report for Q3 earnings?"

        return current_query

enricher = QueryEnricher()
history = [
    {"role": "user", "content": "How is Apple doing this year?"},
    {"role": "assistant", "content": "Apple has seen steady growth, driven by services."},
    {"role": "user", "content": "What did they report for Q3?"}
]

raw_query = history[-1]["content"]
enriched_query = enricher.enrich_query(history[:-1], raw_query)

print("--- Query Enrichment Example ---")
print(f"Raw Query: {raw_query}")
print(f"Enriched Query: {enriched_query}")
