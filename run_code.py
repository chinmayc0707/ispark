import random
import math

print("--- PART 2 ---")
def token_allocator(system_tokens, reserve_tokens, memory_entries, conv_turns, doc_chunks):
    MAX_TOKENS = 16000
    budget = MAX_TOKENS - system_tokens - reserve_tokens

    mem_usage = sum(m['tokens'] for m in memory_entries)
    available_for_dynamic = budget - mem_usage

    while True:
        conv_usage = sum(c['tokens'] for c in conv_turns)
        doc_usage = sum(d['tokens'] for d in doc_chunks)
        total_dynamic = conv_usage + doc_usage

        if total_dynamic <= available_for_dynamic:
            break

        if len(doc_chunks) > 0:
            doc_chunks.pop() # Trim least relevant document chunk first
        elif len(conv_turns) > 0:
            conv_turns.pop(0) # Trim oldest conversation turn next
        else:
            break

    return conv_turns, doc_chunks

convs = [{'id': f'turn_{i+1}', 'tokens': 300} for i in range(12)]
docs = [{'id': f'doc_{i+1}', 'tokens': 500} for i in range(8)]
mems = [{'id': 'mem_1', 'tokens': 150}]

print(f"Scenario 1: {len(convs)} turns ({sum(c['tokens'] for c in convs)} tokens), {len(docs)} chunks ({sum(d['tokens'] for d in docs)} tokens)")
res_convs, res_docs = token_allocator(800, 1000, mems, convs.copy(), docs.copy())
print(f"Result: {len(res_convs)} turns, {len(res_docs)} chunks")

convs_large = [{'id': f'turn_{i+1}', 'tokens': 300} for i in range(20)]
docs_large = [{'id': f'doc_{i+1}', 'tokens': 500} for i in range(20)]
print(f"Scenario 2: {len(convs_large)} turns ({sum(c['tokens'] for c in convs_large)} tokens), {len(docs_large)} chunks ({sum(d['tokens'] for d in docs_large)} tokens)")
res_convs2, res_docs2 = token_allocator(800, 1000, mems, convs_large.copy(), docs_large.copy())
print(f"Result: {len(res_convs2)} turns, {len(res_docs2)} chunks")

print("\n--- PART 3 ---")
class Agent:
    def __init__(self):
        self.tools = {
            "search_codebase": self.search_codebase,
            "search_security_docs": self.search_security_docs,
            "get_file_history": self.get_file_history
        }
        self.trace = []

    def search_codebase(self, query):
        return 'Found function `authenticate_user(token)` in `src/auth.py`. It decodes the JWT and checks expiry.'

    def search_security_docs(self, query):
        if "authenticate_user" in query:
            return 'Warning: `authenticate_user` does not verify the JWT issuer (CVE-2023-XYZ). Vulnerable to spoofing.'
        return 'No vulnerabilities found.'

    def get_file_history(self, filepath, entity):
        return '`src/auth.py` was last modified 14 days ago by alice@example.com.'

    def run(self, user_query):
        self.trace.append("Thought: The user wants to find the authentication function. I need to search the codebase for 'authentication function'.")
        self.trace.append("Action: search_codebase(query='authentication function')")
        obs1 = self.tools["search_codebase"]('authentication function')
        self.trace.append(f"Observation: {obs1}")

        self.trace.append("Thought: I found `authenticate_user` in `src/auth.py`. It decodes JWT and checks expiry. Now I need to check for known vulnerabilities based on security documentation.")
        self.trace.append("Action: search_security_docs(query='authenticate_user src/auth.py vulnerabilities')")
        obs2 = self.tools["search_security_docs"]('authenticate_user src/auth.py vulnerabilities')
        self.trace.append(f"Observation: {obs2}")

        self.trace.append("Thought: The documentation indicates a known vulnerability where it doesn't verify the JWT issuer. Finally, I need to check how long ago `src/auth.py` was modified.")
        self.trace.append("Action: get_file_history(filepath='src/auth.py', entity='authenticate_user')")
        obs3 = self.tools["get_file_history"]('src/auth.py', 'authenticate_user')
        self.trace.append(f"Observation: {obs3}")

        self.trace.append("Thought: I have all the necessary information. I will now synthesize the final response to the user.")
        self.trace.append("Action: OutputFinalResponse()")
        final_answer = "The authentication function `authenticate_user(token)` is located in `src/auth.py`. It decodes the JWT and checks expiry. According to the security documentation, it has a known vulnerability: it does not verify the JWT issuer, making it vulnerable to spoofing. The file was last modified 14 days ago."
        self.trace.append(f"Observation: {final_answer}")

        for t in self.trace:
            print(t)

Agent().run("Find the authentication function in our codebase...")

print("\n--- PART 4 ---")
def dot_product(v1, v2):
    return sum(x*y for x,y in zip(v1,v2))

def magnitude(v):
    return math.sqrt(sum(x*x for x in v))

def cosine_similarity(v1, v2):
    return dot_product(v1, v2) / (magnitude(v1) * magnitude(v2))

def threshold_filter(query_embedding, document_embeddings, threshold):
    results = []
    for doc, emb in document_embeddings.items():
        sim = cosine_similarity(query_embedding, emb)
        if sim >= threshold:
            results.append((doc, sim))
    return sorted(results, key=lambda x: x[1], reverse=True)

random.seed(42)
query_1_emb = [random.random() for _ in range(10)]
docA_emb = [q + random.random() * 0.1 for q in query_1_emb]
docB_emb = [q + random.random() * 0.5 for q in query_1_emb]
docC_emb = [random.random() for _ in range(10)]

docs = {
    "Doc_A_Exact_Match": docA_emb,
    "Doc_B_Partial_Match": docB_emb,
    "Doc_C_Unrelated": docC_emb
}

print("Threshold 0.65:")
res_65 = threshold_filter(query_1_emb, docs, 0.65)
for r in res_65:
    print(f" - {r[0]} (Score: {r[1]:.4f})")

print("\nThreshold 0.80:")
res_80 = threshold_filter(query_1_emb, docs, 0.80)
for r in res_80:
    print(f" - {r[0]} (Score: {r[1]:.4f})")
