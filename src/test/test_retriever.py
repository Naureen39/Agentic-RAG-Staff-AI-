from src.graph_builder.build_graph import build_knowledge_graph
from src.retriever.graph_retriever import GraphRetriever

# Build graph
graph, relations = build_knowledge_graph()

# Init retriever
retriever = GraphRetriever(graph, relations)

# Test query
result = retriever.retrieve("Payment service kis per depend karti hai?")

print("\n=== RETRIEVER OUTPUT ===")
print("Closest Entity:", result["closest_entity"])
print("Related Nodes:", result["related_nodes"])
