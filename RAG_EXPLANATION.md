# Implementing a RAG-based Solution for Internal Knowledge Base

Here is the breakdown of building and testing a Retrieval-Augmented Generation (RAG) system to fix the knowledge retrieval failures at the company.

---

### Task 1: Diagnose the Keyword Search Failure

**Query:** "Why is the device making a buzzing noise?"
**Document:** "Abnormal acoustic vibrations during operation may indicate loose internal components or bearing wear."

**Output of Keyword Search vs Semantic Search:**
```
Keyword Search Overlap Tokens: set(), Score: 0
Semantic Search Cosine Similarity Score: 0.3369
```

**Explanation:**
The keyword search fails completely (score of 0) because there are no overlapping words between the query and the document (excluding common stop words like "is", "the", etc.). The user asked about a "buzzing noise," but the technical documentation uses professional terminology like "acoustic vibrations." Keyword search is literal; it only looks for exact strings.

For a support engineer trying to help a customer, this means that unless the customer perfectly guesses the exact terminology used by the technical writers, the system won't surface the correct document. The engineer is left either blindly guessing different search terms or giving the customer an incorrect answer, leading to a poor customer experience. Semantic search succeeds because it captures the *meaning* of the phrases—it understands that "buzzing noise" and "acoustic vibrations" are conceptually related.

---

### Task 2: Build the Chunking Pipeline

**Paragraph Chosen:**
"The thermal management subsystem utilizes a closed-loop liquid cooling architecture to maintain optimal operating temperatures. Coolant is pumped through a series of micro-channels embedded in the primary heatsink, absorbing thermal energy from the high-power processing units. This heated coolant then flows to the external radiator assembly, where variable-speed fans dissipate the heat into the surrounding environment. To prevent galvanic corrosion and ensure long-term reliability, a specialized dielectric fluid with corrosion inhibitors must be used. Routine maintenance requires checking the fluid reservoir level and inspecting all quick-disconnect fittings for micro-leaks every 500 operating hours."

**Fixed-Size Chunks (Size=150 chars, Overlap=30 chars):**
* **Chunk 1:** `The thermal management subsystem utilizes a closed-loop liquid cooling architecture to maintain optimal operating temperatures. Coolant is pumped thro`
* **Chunk 2:** `atures. Coolant is pumped through a series of micro-channels embedded in the primary heatsink, absorbing thermal energy from the high-power processing`
* **Chunk 3:** `from the high-power processing units. This heated coolant then flows to the external radiator assembly, where variable-speed fans dissipate the heat i`

**Sentence-Aware Chunks (Size=2 sentences, Overlap=1 sentence):**
* **Chunk 1:** `The thermal management subsystem utilizes a closed-loop liquid cooling architecture to maintain optimal operating temperatures. Coolant is pumped through a series of micro-channels embedded in the primary heatsink, absorbing thermal energy from the high-power processing units.`
* **Chunk 2:** `Coolant is pumped through a series of micro-channels embedded in the primary heatsink, absorbing thermal energy from the high-power processing units. This heated coolant then flows to the external radiator assembly, where variable-speed fans dissipate the heat into the surrounding environment.`

**Explanation:**
Sentence-aware chunking preserves meaning much better for dense technical content. Fixed-size chunking blindly slices text mid-word (e.g., "thro", "atures", "heat i") and mid-sentence, destroying the context and syntax required for an LLM to accurately embed or comprehend the text.

Overlap at chunk boundaries is crucial in both methods, but particularly in sentence chunking, because complex technical ideas often span multiple sentences. Overlap ensures that a pronoun or reference in the second sentence maintains its context from the preceding sentence, preventing orphaned information that an embedding model would misinterpret.

---

### Task 3: Build and Query the Vector Store

*(Note: In the absence of an available Gemini API key in the environment, `sentence-transformers/all-MiniLM-L6-v2` was utilized to generate 384-dimensional semantic embeddings to simulate the Gemini embedding behavior.)*

**Query:** "How do I fix the humming sound?"

**Top 3 Retrieved Chunks:**
```
Rank 1 | Score: 0.5376 | Chunk: For resolving the buzzing noise, check the internal acoustic dampers and ensure all mounting screws are torqued to 5Nm.
Rank 2 | Score: 0.1699 | Chunk: The primary heatsink must be cleaned using compressed air and a non-abrasive brush to prevent thermal throttling.
Rank 3 | Score: 0.1508 | Chunk: If the device fails to boot, verify that the internal 12V rail is providing stable power and check the diagnostic LEDs on the mainboard.
```

**Explanation:**
The scores represent the **Cosine Similarity** between the embedded user query and the embedded document chunks. A score closer to 1.0 means the vectors point in nearly the same direction in the high-dimensional space (highly semantically related), while a score near 0 means they are orthogonal (unrelated).

The highest-scoring chunk (0.5376) was selected because its semantic meaning ("resolving the buzzing noise") is extremely close to the user's query ("fix the humming sound"). Despite having completely different vocabularies, the vector math correctly identified that both texts discuss troubleshooting an unwanted audio output.

---

### Task 4: End-to-End Pipeline with Grounded Generation

**Diagram of Pipeline:**
```
  [User Query]
       │
       ▼
 [Embedding Model] ───> Query Vector ──┐
                                       │
                                       ▼
[Document DB] ──> [Chunker] ──> [Vector DB (FAISS)]
                                       │
                                       ▼ (Top K Chunks)
                                       │
                               [Prompt Builder] <── (Context + Query)
                                       │
                                       ▼
                                [LLM Generator]
                                       │
                                       ▼
                                [Final Answer]
```

**Pipeline Execution:**
```
Constructed Prompt:
----------------------------------------
You are a helpful technical support assistant.
Answer the user's question based strictly on the provided context.
If the answer cannot be found in the context, reply exactly with: "I'm sorry, I cannot find the answer in the provided documents."

Context:
- For resolving the buzzing noise, check the internal acoustic dampers and ensure all mounting screws are torqued to 5Nm.
- The primary heatsink must be cleaned using compressed air and a non-abrasive brush to prevent thermal throttling.
- If the device fails to boot, verify that the internal 12V rail is providing stable power and check the diagnostic LEDs on the mainboard.

Question: How do I fix the humming sound?
Answer:
----------------------------------------

Generated Output:
To resolve the buzzing noise, check the internal acoustic dampers and ensure all mounting screws are torqued to 5Nm.
```

---

### Task 5: Reflection

A direct LLM query relies entirely on the model's pre-trained, static knowledge base, meaning it can hallucinate answers, provide outdated information, or completely fail if the topic is a proprietary company manual it was never trained on. A RAG-based query fundamentally changes this paradigm by turning the LLM from a "memorizer" into a "reader." In RAG, the LLM is fed exact, retrieved chunks from the company's internal knowledge base and instructed to synthesize an answer based *only* on that specific context, drastically reducing hallucinations and ensuring the information is proprietary and up-to-date.

However, it is critical to understand that the confidence of an LLM answer is not the same as its correctness. LLMs are trained to generate highly probable sequences of text, which means they write with a tone of absolute certainty regardless of whether the statement is factually true or completely fabricated. An LLM might confidently combine two unrelated troubleshooting steps from different retrieved chunks if the prompt constraints aren't strict enough, sounding authoritative while delivering a broken or dangerous instruction.

Because of this, even in a well-built RAG system, human review remains necessary—especially in high-stakes environments like technical support. Humans must still review the initial quality of the source documents (garbage in, garbage out), manually tune the chunking strategies if tables or diagrams are being mangled, and spot-check edge-case queries where the semantic search retrieves technically similar but contextually incorrect chunks (e.g., retrieving a "pump buzzing" manual when the user meant "fan buzzing"). The LLM accelerates the workflow, but the human engineer ensures the physical reality matches the text.
