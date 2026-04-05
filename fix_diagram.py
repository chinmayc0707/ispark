with open("generate_assignment.py", "r") as f:
    content = f.read()

import re

new_diagram_code = r"""
def generate_diagram():
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
    ax.axis('off')

    # Draw boxes
    boxes = {
        "Input Handler": (0.2, 0.7),
        "Memory Module": (0.5, 0.9),
        "LLM Reasoning\nController": (0.5, 0.5),
        "RAG Retrieval\nPipeline": (0.8, 0.9),
        "Tool Executor": (0.8, 0.5),
        "Output Formatter": (0.5, 0.1)
    }

    box_w = 0.2
    box_h = 0.15

    for label, (x, y) in boxes.items():
        rect = patches.FancyBboxPatch((x - box_w/2, y - box_h/2), box_w, box_h,
                                      boxstyle="round,pad=0.05",
                                      edgecolor="#00529B", facecolor="#E6F2FF", lw=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha="center", va="center", size=10, fontweight="bold")

    # Arrows
    def draw_arrow(start_box, end_box, offset_start=(0,0), offset_end=(0,0), connection="arc3,rad=0"):
        x1, y1 = boxes[start_box]
        x2, y2 = boxes[end_box]

        # Add offsets
        x1 += offset_start[0]; y1 += offset_start[1]
        x2 += offset_end[0]; y2 += offset_end[1]

        ax.annotate("", xy=(x2, y2), xycoords='data',
                    xytext=(x1, y1), textcoords='data',
                    arrowprops=dict(arrowstyle="->", color="gray", lw=2, connectionstyle=connection))

    # Input to Controller
    draw_arrow("Input Handler", "LLM Reasoning\nController", offset_start=(box_w/2, -0.05), offset_end=(-box_w/2, 0.15))

    # Controller to Memory and back
    draw_arrow("LLM Reasoning\nController", "Memory Module", offset_start=(-0.05, box_h/2), offset_end=(-0.05, -box_h/2))
    draw_arrow("Memory Module", "LLM Reasoning\nController", offset_start=(0.05, -box_h/2), offset_end=(0.05, box_h/2))

    # Controller to RAG and back
    draw_arrow("LLM Reasoning\nController", "RAG Retrieval\nPipeline", offset_start=(0.08, 0.08), offset_end=(-0.08, -0.08), connection="arc3,rad=0.1")
    draw_arrow("RAG Retrieval\nPipeline", "LLM Reasoning\nController", offset_start=(-0.1, -0.05), offset_end=(0.1, 0.05), connection="arc3,rad=0.1")

    # Controller to Tool and back
    draw_arrow("LLM Reasoning\nController", "Tool Executor", offset_start=(box_w/2, 0.05), offset_end=(-box_w/2, 0.05))
    draw_arrow("Tool Executor", "LLM Reasoning\nController", offset_start=(-box_w/2, -0.05), offset_end=(box_w/2, -0.05))

    # Controller to Output
    draw_arrow("LLM Reasoning\nController", "Output Formatter", offset_start=(0, -box_h/2), offset_end=(0, box_h/2))

    plt.title("System Architecture Diagram", fontsize=16, fontweight='bold', y=1.0)
    plt.savefig("architecture_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()
"""

content = re.sub(r'def generate_diagram\(\):.*?plt\.close\(\)', new_diagram_code.strip(), content, flags=re.DOTALL)

with open("generate_assignment.py", "w") as f:
    f.write(content)
