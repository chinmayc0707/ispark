import matplotlib.pyplot as plt
import networkx as nx

plt.xkcd()

G = nx.DiGraph()

nodes = [
    "Input\nHandler",
    "Memory\nModule",
    "RAG Retrieval\nPipeline",
    "LLM Reasoning\nController",
    "Tool\nExecutor",
    "Output\nFormatter"
]

G.add_edges_from([
    ("Input\nHandler", "LLM Reasoning\nController"),
    ("LLM Reasoning\nController", "Memory\nModule"),
    ("Memory\nModule", "LLM Reasoning\nController"),
    ("LLM Reasoning\nController", "RAG Retrieval\nPipeline"),
    ("RAG Retrieval\nPipeline", "LLM Reasoning\nController"),
    ("LLM Reasoning\nController", "Tool\nExecutor"),
    ("Tool\nExecutor", "LLM Reasoning\nController"),
    ("LLM Reasoning\nController", "Output\nFormatter")
])

pos = {
    "Input\nHandler": (0, 2),
    "Memory\nModule": (2, 3.5),
    "RAG Retrieval\nPipeline": (4, 3.5),
    "Tool\nExecutor": (3, 0.5),
    "LLM Reasoning\nController": (2, 2),
    "Output\nFormatter": (4, 2)
}

fig, ax = plt.subplots(figsize=(10, 6))
nx.draw(G, pos, with_labels=True, node_size=5000, node_color="lightblue",
        font_size=10, font_weight="bold", arrows=True, ax=ax,
        edge_color="gray", node_shape="o")

plt.title("Agentic AI System Architecture (Hand-drawn style)")
plt.savefig("architecture_diagram.png", bbox_inches='tight')
