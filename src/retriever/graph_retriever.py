import networkx as nx
import numpy as np
from langchain_ollama import OllamaEmbeddings

class GraphRetriever:
    def __init__(self, graph, merged_relations, embedding_model="nomic-embed-text"):
        """
        Graph retriever initialize karta hai.
        - graph: NetworkX Directed Graph
        - merged_relations: entity dependency mapping
        - embedding_model: Ollama embeddings model
        """

        self.graph = graph
        self.merged_relations = merged_relations
        self.emb = OllamaEmbeddings(model=embedding_model)

        print("[Retriever] Embedding model loaded:", embedding_model)

        # Precompute embeddings for all nodes
        self.entity_embeddings = self._embed_entities(list(graph.nodes()))

    def _embed_entities(self, entities):
        """
        Har entity ka embedding generate karke dictionary me store karo.
        """
        if not entities:
            return {}
        embeddings = self.emb.embed_documents(entities)
        return {ent: np.array(vec) for ent, vec in zip(entities, embeddings)}

    def embed_query(self, query):
        """
        User query ka embedding.
        """
        return np.array(self.emb.embed_query(query))

    def find_closest_entity(self, query_vector):
        """
        Query embedding se sabse close entity find karta hai.
        """

        best_entity = None
        best_score = -999

        for entity, emb in self.entity_embeddings.items():
            denom = np.linalg.norm(query_vector) * np.linalg.norm(emb)
            if denom == 0:
                continue
            score = np.dot(query_vector, emb) / denom

            if score > best_score:
                best_score = score
                best_entity = entity

        return best_entity, best_score

    def multi_hop_traverse(self, start_entity, hops=2):
        """
        Graph me multi-hop traversal.
        start_entity -> neighbors -> neighbors of neighbors
        """

        visited = set()
        frontier = {start_entity}

        for _ in range(hops):
            next_frontier = set()
            for node in frontier:
                visited.add(node)
                neighbors = list(self.graph.predecessors(node)) + list(self.graph.successors(node))
                next_frontier.update(neighbors)
            frontier = next_frontier

        return list(visited)

    def retrieve(self, query, hops=2):
        """
        Final retriever function:
        - Query embedding
        - Closest entity
        - Multi-hop nodes
        """

        if not self.entity_embeddings:
            raise ValueError("Graph has no entities to retrieve from.")

        q_vec = self.embed_query(query)
        closest_entity, score = self.find_closest_entity(q_vec)

        if closest_entity is None:
            raise ValueError("No matching entity found for query.")

        print(f"[Retriever] Closest entity: {closest_entity}  (score={score:.4f})")

        # Multi-hop graph expansion
        related_nodes = self.multi_hop_traverse(closest_entity, hops=hops)

        return {
            "query": query,
            "closest_entity": closest_entity,
            "related_nodes": related_nodes,
        }
