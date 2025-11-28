from src.graph_builder.build_graph import build_knowledge_graph
from src.graph_builder.save_graph import save_graph_as_json

graph, relations = build_knowledge_graph()
save_graph_as_json(graph, relations)
