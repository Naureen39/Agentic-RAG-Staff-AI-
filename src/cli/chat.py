from src.agent.workflow import build_app

def main():
    app = build_app()

    print("=== Agentic RAG Chat ===")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ")

        if query.lower().strip() in ("exit", "quit"):
            break

        state = {
            "query": query,
            "steps": [],
            "tools_used": [],
            "nodes_traversed": []
        }

        result = app.invoke(state)

        print("\nAssistant:", result.get("answer"))
        print("\n--- Debug Info ---")
        print("Steps:", result.get("steps"))
        print("Tools used:", result.get("tools_used"))
        print("Nodes traversed:", result.get("nodes_traversed"))
        print("----------------------\n")


if __name__ == "__main__":
    main()
