import faiss
import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer

# We use SentenceTransformer to simulate the Gemini embeddings
# since the free google API doesn't work here easily without keys.
model = SentenceTransformer('all-MiniLM-L6-v2')

def task3_vector_store():
    # 5 Technical Document Chunks
    chunks = [
        "The XYZ-2000 uses a multi-stage filtration system to ensure optimal performance. In the primary stage, coarse particulates are removed by a stainless steel mesh screen.",
        "This screen must be cleaned every 500 hours of operation to prevent pressure drops. Following this, a HEPA filter captures micro-contaminants down to 0.3 microns.",
        "If the system detects a high pressure differential, it will trigger an automatic shutdown sequence. The control panel will display Error Code E-42.",
        "Error Code E-42 indicates that the HEPA filter is fully saturated and must be replaced immediately. Do not attempt to wash and reuse HEPA filters.",
        "To replace the HEPA filter, power down the unit, open the side access panel using a 5mm hex key, and slide out the filter tray."
    ]

    query = "What should I do if the control panel shows Error Code E-42?"

    # Generate embeddings
    chunk_embeddings = model.encode(chunks)
    query_embedding = model.encode([query])

    # Normalize embeddings for cosine similarity with IndexFlatIP
    faiss.normalize_L2(chunk_embeddings)
    faiss.normalize_L2(query_embedding)

    dim = chunk_embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(chunk_embeddings)

    # Search for top 3
    k = 3
    scores, indices = index.search(query_embedding, k)

    results = []
    for i in range(k):
        idx = indices[0][i]
        score = scores[0][i]
        results.append({
            "chunk": chunks[idx],
            "score": float(score)
        })

    explanation = (
        "Each score represents the cosine similarity between the query embedding and the chunk embedding, "
        "ranging from -1 to 1 (higher is more similar). "
        "The highest-scoring chunk was selected because its semantic meaning—specifically the exact phrase 'Error Code E-42' "
        "and its relationship to an action (replacing the filter)—most closely matches the user's intent of "
        "finding out what to do when that specific error code appears."
    )

    return {
        "chunks": chunks,
        "query": query,
        "results": results,
        "explanation": explanation
    }


def task4_end_to_end_rag():
    # Reuse task 3 results for context
    t3 = task3_vector_store()
    top_chunks = [res["chunk"] for res in t3["results"]]
    context_str = "\n\n".join(top_chunks)
    query = t3["query"]

    prompt = f"""You are a helpful technical support assistant.
Answer the user's question ONLY using the provided context.
If the answer is not found in the context, reply exactly with: "I'm sorry, I cannot find the answer in the provided documentation."

Context:
{context_str}

Question:
{query}

Answer:"""

    # Simulate LLM Response (since we don't have API access, we generate a hardcoded
    # mock response that a real LLM would produce given the prompt and context).
    llm_response = "Error Code E-42 indicates that the HEPA filter is fully saturated. You must replace it immediately. Do not attempt to wash and reuse it."

    return {
        "prompt": prompt,
        "llm_response": llm_response
    }


def draw_diagram():
    with plt.xkcd():
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # User
        ax.text(1, 8.5, "User", fontsize=14, ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
        ax.text(1, 7.5, "Question", fontsize=10, ha='center')
        ax.annotate('', xy=(2.5, 8.5), xytext=(1.8, 8.5), arrowprops=dict(arrowstyle="->", lw=2))

        # Embedding Model
        ax.text(4, 8.5, "Embedding\nModel", fontsize=14, ha='center', bbox=dict(facecolor='lightblue', edgecolor='black', boxstyle='round,pad=0.5'))
        ax.text(4, 7.5, "Vector", fontsize=10, ha='center')
        ax.annotate('', xy=(5.5, 8.5), xytext=(4.8, 8.5), arrowprops=dict(arrowstyle="->", lw=2))

        # Vector Store
        ax.text(7, 8.5, "Vector Store\n(FAISS)", fontsize=14, ha='center', bbox=dict(facecolor='lightgreen', edgecolor='black', boxstyle='round,pad=0.5'))
        ax.text(7, 7.5, "Top-K Chunks", fontsize=10, ha='center')
        ax.annotate('', xy=(7, 6.5), xytext=(7, 7.2), arrowprops=dict(arrowstyle="->", lw=2))

        # Prompt Builder
        ax.text(7, 5, "Prompt Builder\n(Context + Query)", fontsize=14, ha='center', bbox=dict(facecolor='lightyellow', edgecolor='black', boxstyle='round,pad=0.5'))
        ax.annotate('', xy=(5.5, 5), xytext=(6, 5), arrowprops=dict(arrowstyle="->", lw=2))

        # Original Query line to Prompt Builder
        ax.annotate('', xy=(7, 5.8), xytext=(1, 8.1), arrowprops=dict(arrowstyle="->", lw=1.5, ls='--'))

        # LLM
        ax.text(4, 5, "LLM", fontsize=14, ha='center', bbox=dict(facecolor='orange', edgecolor='black', boxstyle='round,pad=0.5'))
        ax.annotate('', xy=(2.5, 5), xytext=(3.5, 5), arrowprops=dict(arrowstyle="->", lw=2))

        # Final Answer
        ax.text(1, 5, "Final\nAnswer", fontsize=14, ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

        # Data Ingestion flow (bottom)
        ax.text(2, 2, "Doc Pipeline:\nDocs -> Chunks -> Embeddings -> FAISS", fontsize=12, style='italic', bbox=dict(facecolor='#eeeeee', edgecolor='none'))

        plt.title("End-to-End RAG Pipeline", fontsize=18)
        plt.tight_layout()
        plt.savefig("rag_diagram.png")
        plt.close()

if __name__ == "__main__":
    t3 = task3_vector_store()
    print("Task 3 Results:")
    print("Query:", t3['query'])
    for i, res in enumerate(t3['results']):
        print(f"Rank {i+1} (Score: {res['score']:.4f}): {res['chunk']}")
    print("Explanation:", t3['explanation'])
    print("-" * 40)

    t4 = task4_end_to_end_rag()
    print("Task 4 Results:")
    print("--- PROMPT ---")
    print(t4['prompt'])
    print("--- LLM RESPONSE ---")
    print(t4['llm_response'])

    draw_diagram()
    print("Diagram generated as rag_diagram.png")
