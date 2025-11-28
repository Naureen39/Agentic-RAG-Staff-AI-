from src.ingest.entity_extractor import build_entity_relation

sample = """
Payment Service depends on AuthenticationService.
AuthenticationService uses UserDatabase.
"""

print(build_entity_relation(sample))
