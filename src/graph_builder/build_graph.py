from src.ingest.loader import load_documents
from src.ingest.entity_extractor import build_entity_relation
from src.graph_builder.graph_utils import merge_relations, create_graph


def build_knowledge_graph():
    """
    Poora KG pipeline:
    1) Documents load
    2) Relations extract
    3) Merge relations
    4) Graph create
    """

    docs = load_documents("data")

    extracted_relations = []

    for doc in docs:
        relations = build_entity_relation(doc["content"])
        extracted_relations.append(relations)

    merged = merge_relations(extracted_relations)
    graph = create_graph(merged)

    print("[Graph] Knowledge Graph Build Complete!")
    print(f"[Graph] Total Nodes: {len(graph.nodes())}")
    print(f"[Graph] Total Edges: {len(graph.edges())}")

    return graph, merged
