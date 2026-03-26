import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Download punkt tokenizer for sentence chunking
nltk.download('punkt')
nltk.download('punkt_tab')

def task1_keyword_vs_semantic():
    query = "Why is the device making a buzzing noise?"
    document = "Abnormal acoustic vibrations during operation may indicate loose internal components or bearing wear."

    # 1. Keyword Search
    import string
    def normalize(text):
        return text.translate(str.maketrans('', '', string.punctuation)).lower()

    q_tokens = set(normalize(query).split())
    d_tokens = set(normalize(document).split())

    keyword_overlap = q_tokens.intersection(d_tokens)
    keyword_score = len(keyword_overlap) / len(q_tokens) if q_tokens else 0.0

    # 2. Semantic Search
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([query, document])

    q_emb = embeddings[0].reshape(1, -1)
    d_emb = embeddings[1].reshape(1, -1)

    semantic_score = cosine_similarity(q_emb, d_emb)[0][0]

    explanation = (
        "Keyword search fails here because there is absolutely no vocabulary overlap between "
        "the query ('buzzing', 'noise') and the document ('acoustic', 'vibrations'). "
        "They use completely different words to describe the same physical phenomenon. "
        "For a support engineer trying to help a customer, this means that unless the engineer "
        "guesses the exact formal terminology used in the manual, they won't find the answer, "
        "leading to delays or incorrect advice."
    )

    return {
        "query": query,
        "document": document,
        "keyword_overlap": list(keyword_overlap),
        "keyword_score": keyword_score,
        "semantic_score": float(semantic_score),
        "explanation": explanation
    }

def task2_chunking():
    paragraph = (
        "The XYZ-2000 uses a multi-stage filtration system to ensure optimal performance. "
        "In the primary stage, coarse particulates are removed by a stainless steel mesh screen. "
        "This screen must be cleaned every 500 hours of operation to prevent pressure drops. "
        "Following this, a HEPA filter captures micro-contaminants down to 0.3 microns. "
        "If the system detects a high pressure differential, it will trigger an automatic shutdown sequence."
    )

    # Fixed-size chunking (e.g., 100 characters with 20 overlap)
    fixed_chunks = []
    chunk_size = 100
    overlap = 20

    start = 0
    while start < len(paragraph):
        end = start + chunk_size
        fixed_chunks.append(paragraph[start:end])
        start += chunk_size - overlap

    # Sentence-aware chunking (e.g., chunk by 2 sentences with 1 sentence overlap)
    sentences = nltk.tokenize.sent_tokenize(paragraph)
    sentence_chunks = []

    for i in range(len(sentences) - 1):
        chunk = sentences[i] + " " + sentences[i+1]
        sentence_chunks.append(chunk)
    if len(sentences) > 0 and len(sentences) == 1:
        sentence_chunks.append(sentences[0])

    explanation = (
        "Sentence-aware chunking preserves meaning much better for dense technical content. "
        "Fixed-size chunking arbitrarily cuts words or sentences in half (e.g., cutting off in the middle of a word), "
        "which destroys the semantic context needed by embedding models to accurately represent the text. "
        "Sentence-aware chunking keeps complete, coherent thoughts together. "
        "Overlap at chunk boundaries matters because a single concept might span across two sentences or be located at the edges of a chunk; "
        "overlap ensures no critical context (like a cause-and-effect relationship) is split entirely into two disconnected vectors."
    )

    return {
        "paragraph": paragraph,
        "fixed_chunks": fixed_chunks,
        "sentence_chunks": sentence_chunks,
        "explanation": explanation
    }

if __name__ == "__main__":
    t1 = task1_keyword_vs_semantic()
    print("Task 1 Results:")
    print("Query:", t1['query'])
    print("Document:", t1['document'])
    print("Keyword Score:", t1['keyword_score'])
    print("Semantic Score:", t1['semantic_score'])
    print("Explanation:", t1['explanation'])
    print("-" * 40)

    t2 = task2_chunking()
    print("Task 2 Results:")
    print("Fixed Chunks:")
    for i, c in enumerate(t2['fixed_chunks']):
        print(f"  [{i}] {c}")
    print("\nSentence Chunks:")
    for i, c in enumerate(t2['sentence_chunks']):
        print(f"  [{i}] {c}")
    print("\nExplanation:", t2['explanation'])
