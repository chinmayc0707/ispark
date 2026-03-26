import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import re

print("--- Task 1: Keyword vs Semantic Search ---\n")
query_1 = "Why is the device making a buzzing noise?"
doc_1 = "Abnormal acoustic vibrations during operation may indicate loose internal components or bearing wear."

# Keyword Search implementation
def keyword_search(query, document):
    # simple lowercase and split by non-word characters
    query_tokens = set(re.findall(r'\b\w+\b', query.lower()))
    doc_tokens = set(re.findall(r'\b\w+\b', document.lower()))
    # Remove common stopwords to be fair
    stopwords = {"is", "the", "a", "why"}
    query_tokens = query_tokens - stopwords

    overlap = query_tokens.intersection(doc_tokens)
    return overlap, len(overlap)

overlap_tokens, score_keyword = keyword_search(query_1, doc_1)
print(f"Query: {query_1}")
print(f"Document: {doc_1}")
print(f"Keyword Search Overlap Tokens: {overlap_tokens}, Score: {score_keyword}")

# Semantic Search Implementation
model = SentenceTransformer('all-MiniLM-L6-v2')
# We use this to simulate Gemini embeddings due to missing API keys.
# The dimensions are 384 for all-MiniLM-L6-v2.

query_emb = model.encode([query_1])[0]
doc_emb = model.encode([doc_1])[0]

# Compute cosine similarity
cos_sim = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
print(f"Semantic Search Cosine Similarity Score: {cos_sim:.4f}")
print("\n")


print("--- Task 2: Chunking Pipeline ---\n")
paragraph = (
    "The thermal management subsystem utilizes a closed-loop liquid cooling architecture to maintain optimal operating temperatures. "
    "Coolant is pumped through a series of micro-channels embedded in the primary heatsink, absorbing thermal energy from the high-power processing units. "
    "This heated coolant then flows to the external radiator assembly, where variable-speed fans dissipate the heat into the surrounding environment. "
    "To prevent galvanic corrosion and ensure long-term reliability, a specialized dielectric fluid with corrosion inhibitors must be used. "
    "Routine maintenance requires checking the fluid reservoir level and inspecting all quick-disconnect fittings for micro-leaks every 500 operating hours."
)

def fixed_size_chunking(text, chunk_size=150, overlap=30):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def sentence_aware_chunking(text, max_sentences=2, overlap=1):
    # Naive sentence splitting
    sentences = [s.strip() for s in text.split('. ') if s]
    # Add back the period
    sentences = [s + "." if not s.endswith('.') else s for s in sentences]

    chunks = []
    start = 0
    while start < len(sentences):
        chunk = " ".join(sentences[start:start + max_sentences])
        chunks.append(chunk)
        start += max_sentences - overlap
    return chunks

fixed_chunks = fixed_size_chunking(paragraph)
sentence_chunks = sentence_aware_chunking(paragraph)

print("Fixed-Size Chunks:")
for i, c in enumerate(fixed_chunks):
    print(f"Chunk {i+1}: {c}")

print("\nSentence-Aware Chunks:")
for i, c in enumerate(sentence_chunks):
    print(f"Chunk {i+1}: {c}")
print("\n")


print("--- Task 3: Vector Store and Retrieval ---\n")
technical_docs = [
    "Error code E-404 indicates a failure in the secondary pressure valve communication bus.",
    "For resolving the buzzing noise, check the internal acoustic dampers and ensure all mounting screws are torqued to 5Nm.",
    "The primary heatsink must be cleaned using compressed air and a non-abrasive brush to prevent thermal throttling.",
    "If the device fails to boot, verify that the internal 12V rail is providing stable power and check the diagnostic LEDs on the mainboard.",
    "Routine calibration of the optical sensor should be performed using the provided target reticle every 30 days."
]

embeddings = model.encode(technical_docs)
# Normalize for Cosine Similarity in FAISS (Inner Product becomes Cosine Similarity on normalized vectors)
faiss.normalize_L2(embeddings)

# Create FAISS IndexFlatIP (Inner Product)
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)

query_3 = "How do I fix the humming sound?"
query_3_emb = model.encode([query_3])
faiss.normalize_L2(query_3_emb)

k = 3
D, I = index.search(query_3_emb, k)

print(f"Query: {query_3}\n")
print("Top 3 retrieved chunks:")
for i in range(k):
    idx = I[0][i]
    score = D[0][i]
    print(f"Rank {i+1} | Score: {score:.4f} | Chunk: {technical_docs[idx]}")
print("\n")


print("--- Task 4: End-to-End Pipeline with Grounded Generation ---\n")

def generate_prompt(query, retrieved_chunks):
    context = "\n".join([f"- {chunk}" for chunk in retrieved_chunks])
    prompt = f"""You are a helpful technical support assistant.
Answer the user's question based strictly on the provided context.
If the answer cannot be found in the context, reply exactly with: "I'm sorry, I cannot find the answer in the provided documents."

Context:
{context}

Question: {query}
Answer:"""
    return prompt

def mock_llm_generation(prompt):
    # Simple rule-based mock for demonstration since we lack an API key
    if "E-404" in prompt and "communication bus" in prompt:
         return "Error code E-404 indicates a failure in the secondary pressure valve communication bus."
    elif "humming sound" in prompt or "buzzing noise" in prompt:
         return "To resolve the buzzing noise, check the internal acoustic dampers and ensure all mounting screws are torqued to 5Nm."
    else:
         return "I'm sorry, I cannot find the answer in the provided documents."

retrieved_texts = [technical_docs[idx] for idx in I[0]]
final_prompt = generate_prompt(query_3, retrieved_texts)

print("Constructed Prompt:")
print("-" * 40)
print(final_prompt)
print("-" * 40)

print("\nGenerated Output:")
output = mock_llm_generation(final_prompt)
print(output)
print("\n")
