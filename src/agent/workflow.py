from typing import TypedDict, List, Optional, Dict

from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM


from src.graph_builder.build_graph import build_knowledge_graph
from src.retriever.graph_retriever import GraphRetriever


# Build graph + retriever once at startup
graph, relations = build_knowledge_graph()
retriever = GraphRetriever(graph, relations)

# LLM model (reasoning)
llm = OllamaLLM(model="llama3.1")   # <-- Your LLM model


# -----------------------------
#     STATE STRUCTURE
# -----------------------------

class AgentState(TypedDict, total=False):
    query: str
    route: str
    context_nodes: List[str]
    calc_result: Optional[int]
    answer: Optional[str]
    error: Optional[str]
    steps: List[str]
    tools_used: List[str]
    nodes_traversed: List[str]


# -----------------------------
#     ROUTER NODE
# -----------------------------

def router_node(state: AgentState) -> AgentState:
    query = state["query"].lower()

    if "how many" in query or "count" in query:
        route = "calc"
    elif "summarize" in query or "summary" in query:
        route = "summarize"
    else:
        route = "retrieve"

    state["route"] = route

    steps = state.get("steps", [])
    steps.append(f"router:{route}")
    state["steps"] = steps

    return state


def router_decision(state: AgentState):
    return state.get("route", "retrieve")


# -----------------------------
#   RETRIEVER NODE
# -----------------------------

def retriever_node(state: AgentState) -> AgentState:
    result = retriever.retrieve(state["query"])

    context_nodes = result["related_nodes"]
    closest = result["closest_entity"]

    state["context_nodes"] = context_nodes
    state["nodes_traversed"] = context_nodes

    steps = state.get("steps", [])
    steps.append("retriever_node")
    state["steps"] = steps

    tools_used = state.get("tools_used", [])
    tools_used.append("graph_retriever")
    state["tools_used"] = tools_used

    return state


# -----------------------------
#   SUMMARIZE TOOL NODE
# -----------------------------

def summarize_node(state: AgentState) -> AgentState:
    result = retriever.retrieve(state["query"])

    context_nodes = result["related_nodes"]
    state["context_nodes"] = context_nodes
    state["nodes_traversed"] = context_nodes

    tools = state.get("tools_used", [])
    tools.append("summarize_tool")
    state["tools_used"] = tools

    steps = state.get("steps", [])
    steps.append("summarize_node")
    state["steps"] = steps

    return state


# -----------------------------
#   CALC TOOL NODE
# -----------------------------

def calc_node(state: AgentState) -> AgentState:
    result = retriever.retrieve(state["query"])

    entity = result["closest_entity"]
    dependents = list(graph.predecessors(entity))

    state["calc_result"] = len(dependents)
    state["context_nodes"] = [entity] + dependents
    state["nodes_traversed"] = [entity] + dependents

    tools = state.get("tools_used", [])
    tools.append("calc_tool")
    state["tools_used"] = tools

    steps = state.get("steps", [])
    steps.append("calc_node")
    state["steps"] = steps

    return state


# -----------------------------
#   REASONING (LLM) NODE
# -----------------------------

def reasoning_node(state: AgentState) -> AgentState:
    query = state["query"]
    context = state.get("context_nodes", [])
    calc_result = state.get("calc_result", None)

    prompt = f"""
You are an AI reasoning over a service architecture.

User Question:
{query}

Relevant Graph Context:
{context}

"""

    if calc_result is not None:
        prompt += f"\nCount Result: {calc_result}\n"

    prompt += """
Rules:
- Respond based ONLY on provided graph context.
- If an entity does not exist, say you cannot find it.
- Never hallucinate missing services.
"""

    response = llm.invoke(prompt)

    if isinstance(response, str):
        answer = response
    else:
        answer = str(response)

    state["answer"] = answer

    steps = state.get("steps", [])
    steps.append("reasoning_node")
    state["steps"] = steps

    return state


# -----------------------------
#   ERROR HANDLER NODE
# -----------------------------

def error_node(state: AgentState) -> AgentState:
    if state.get("error") and not state.get("answer"):
        state["answer"] = f"Sorry, I couldn't answer because: {state['error']}"

    steps = state.get("steps", [])
    steps.append("error_node")
    state["steps"] = steps

    return state


# -----------------------------
#   BUILD WORKFLOW
# -----------------------------

def build_app():
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("retrieve", retriever_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("calc", calc_node)
    workflow.add_node("reason", reasoning_node)
    workflow.add_node("error", error_node)

    # Start node
    workflow.set_entry_point("router")

    # Conditional routing (without 'default' argument)
    workflow.add_conditional_edges(
        "router",
        router_decision,
        {
            "retrieve": "retrieve",
            "summarize": "summarize",
            "calc": "calc"
        }
    )

    # Flow after tool or retriever
    workflow.add_edge("retrieve", "reason")
    workflow.add_edge("summarize", "reason")
    workflow.add_edge("calc", "reason")

    # Reason → Error → END
    workflow.add_edge("reason", "error")
    workflow.add_edge("error", END)

    return workflow.compile()

