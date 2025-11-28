import networkx as nx

def merge_relations(all_relations):
    """
    Saare documents ke relations ko merge karta hai.
    all_relations = [ {entity: [deps]}, {...}, ... ]
    """
    merged = {}

    for relation in all_relations:
        for entity, deps in relation.items():
            if entity not in merged:
                merged[entity] = set()
            merged[entity].update(deps)

    # Convert sets back to lists
    for k in merged:
        merged[k] = list(merged[k])

    return merged


def create_graph(merged_relations):
    """
    NetworkX graph banata hai entities aur dependencies ke beech.
    """
    G = nx.DiGraph()   # Directed Graph (A depends on B)

    for entity, deps in merged_relations.items():
        G.add_node(entity)
        for dep in deps:
            G.add_node(dep)
            G.add_edge(entity, dep)

    return G
