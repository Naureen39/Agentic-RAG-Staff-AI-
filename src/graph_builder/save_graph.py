import json
import networkx as nx

def save_graph_as_json(graph, merged_relations, path="graph/graph.json"):
    """
    Graph + relations ko JSON file me save karta hai.
    """
    data = {
        "nodes": list(graph.nodes()),
        "edges": list(graph.edges()),
        "relations": merged_relations
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"[Graph] Graph saved to {path}")
