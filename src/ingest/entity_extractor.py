import re

# Normalize entity names (Authentication Service -> AuthenticationService)
def normalize(name):
    return name.replace(" ", "").strip()


def extract_entities(text):
    """
    Entities detect karta hai headings, modules, services, etc. se.
    """

    patterns = [
        r"[A-Z][a-zA-Z]+Service",
        r"[A-Z][a-zA-Z]+Module",
        r"[A-Z][a-zA-Z]+Engine",
        r"[A-Z][a-zA-Z]+Validator",
        r"[A-Z][a-zA-Z]+Generator",
        r"Project\s?[A-Z]",
        r"[A-Z][a-zA-Z]+Database",
    ]

    entities = set()

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            entities.add(normalize(m))

    return list(entities)


def extract_section_dependencies(section_text):
    """
    ## Dependencies
    - UserDatabase
    - EmailService
    """

    lines = section_text.split("\n")

    deps = []
    for line in lines:
        line = line.strip()
        if line.startswith("-"):
            cleaned = line.replace("-", "").strip()
            deps.append(normalize(cleaned))

    return deps


def extract_section(text, header):
    """
    Retrieves text under a Markdown header like:
    ## Dependencies
    ## Used By
    """

    pattern = rf"{header}([\s\S]*?)(##|\Z)"
    match = re.search(pattern, text)

    if match:
        return match.group(1).strip()

    return ""


def build_entity_relation(text):
    entities = extract_entities(text)

    # Detect "Dependencies" section
    dep_section = extract_section(text, r"## Dependencies")
    deps = extract_section_dependencies(dep_section)

    # Detect "Used By" section (reverse relationship)
    used_by_section = extract_section(text, r"## Used By")
    used_by = extract_section_dependencies(used_by_section)

    relations = {}

    # Normal relations
    for ent in entities:
        relations[ent] = deps

    # Reverse relations (UsedBy)
    for user in used_by:
        if user not in relations:
            relations[user] = []
        relations[user].extend(entities)

    return relations
