# Agentic RAG System (Graph-Based Retrieval + LangGraph Agent)

This project implements a small, self-contained Agentic RAG system that reads service-level documentation, builds a knowledge graph, retrieves information through graph-based traversal, and uses a LangGraph agent (powered by a local LLM via Ollama) to answer complex multi-step queries.

The goal of the exercise is to show how a retrieval pipeline can go beyond simple text search by using explicit service relationships such as dependencies and “used-by” links.

The system includes document ingestion, entity extraction, graph construction, a custom graph-aware retriever, a LangGraph workflow with tool-calling, and an interactive CLI for debugging and inspection.

---

## 1. Architecture Overview

This is the overall flow of the system:

/data/*.md (Service documents)
│
▼
Document Loader (load markdown files)
│
▼
Entity Extractor (extract service name, dependencies, used-by)
│
▼
Knowledge Graph (NetworkX) (directed graph of service relationships)
│
▼
GraphRetriever (embeddings + multi-hop traversal)
│
▼
LangGraph Agent

Router Node

Retriever Node

Summarize Tool

Calculation Tool

Reasoning Node (LLaMA 3.1)

Error Handler
│
▼
CLI Chat Interface (answers + full step trace)

yaml
Copy code

The agent uses both symbolic retrieval (graph) and LLM reasoning to produce answers.

---

## 2. Key Features

### Graph-Aware Retrieval
Rather than relying on text similarity alone, retrieval uses an explicit service dependency graph. This allows the system to answer multi-hop questions such as:

- “Which project indirectly depends on the Authentication Service?”
- “What breaks if EmailService goes down?”

### Embedding-Based Matching
User queries are mapped to the closest service using a local embedding model (`nomic-embed-text` through Ollama).

### LangGraph Agent
A transparent multi-step workflow using LangGraph:

- **Router** decides the action based on query  
- **Retriever** collects graph context  
- **Tools** perform summarization and dependency counting  
- **Reasoning node** uses LLaMA 3.1 to produce a final answer  
- **Error node** ensures graceful failures  

### CLI Interface
Helps test the agent by showing:

- Final answer  
- Workflow steps executed  
- Tools invoked  
- Graph nodes traversed  

---

## 3. Project Structure

project/
│
├── data/ # Input service documents
├── graph/ # Saved graph & metadata
│
├── src/
│ ├── ingest/ # Loader, chunker, entity extraction
│ ├── graph_builder/ # Graph construction utilities
│ ├── retriever/ # GraphRetriever implementation
│ ├── agent/ # LangGraph workflow
│ ├── cli/ # CLI interface
│ └── utils/ # Misc helpers
│
├── tests/ # Lightweight test scripts
├── requirements.txt
└── README.md

yaml
Copy code

Everything is modular so components can be tested independently.

---

## 4. How the System Works

### 4.1 Document Ingestion
Markdown files from `/data` are read and parsed.  
Each document must define:

- A service name (H1 heading)  
- A **Dependencies** section  
- A **Used By** section  

These represent the service relationships.

### 4.2 Entity Extraction
The extractor identifies:

- the root entity (document title)  
- lists of dependencies  
- lists of dependents  

Blank or malformed entries are ignored.

### 4.3 Knowledge Graph Construction
A directed graph is created using NetworkX.

Example:

AuthenticationService → UserService
PaymentService → AuthenticationService
ProjectABackend → PaymentService

yaml
Copy code

This graph supports multi-hop traversal.

### 4.4 Graph Retriever
Retrieval combines:

- embedding-based nearest-entity search  
- multi-hop graph expansion  
- neighbors from both predecessors and successors  

This ensures proper recall of related services.

### 4.5 LangGraph Agent
The agent is built as a state machine:

- Router node chooses path (retrieve, summarize, calc)
- Retriever node gets context
- Summarize / Calc tool nodes run when needed
- Reasoning node uses the LLM to answer
- Error node ensures safe fallback

### 4.6 CLI Interface
A small, test-friendly CLI helps evaluate the agent.

---

## 5. Installation

### Install dependencies
pip install -r requirements.txt

makefile
Copy code

### Install Ollama
Download:  
https://ollama.com/download

### Pull required models
ollama pull nomic-embed-text
ollama pull llama3.1

yaml
Copy code

---

## 6. Running the System

### Build the graph
python tests/test_graph.py

shell
Copy code

### Test graph retriever
python tests/test_retriever.py

shell
Copy code

### Launch the agent
python -m src.cli.chat

yaml
Copy code

---

## 7. Example Queries (Suggested for Demonstration)

### Multi-hop reasoning
Which project depends on the AuthenticationService?

shell
Copy code

### Counting dependencies
How many services depend on NotificationService?

shell
Copy code

### Subsystem summarization
Summarize the authentication subsystem.

shell
Copy code

### Error testing
Tell me about the PaymentRouter service.

shell
Copy code

### Impact analysis
What happens if EmailService goes down?

yaml
Copy code

---

## 8. Tools Implemented

### Summarize Tool
Collects the graph neighborhood and provides a subsystem-level summary.

### Calculation Tool
Counts how many services rely on a target service based on incoming graph edges.

### Graph Retriever
Performs entity matching and multi-hop expansion.

---

## 9. Limitations

A few limitations were intentional to keep the system focused:

- Entity extraction uses simple rule-based parsing  
- Retrieval operates at service-level, not chunk-level  
- No persistent vector store  
- Router logic is keyword-based  

The system is built for clarity, not scale.

---

## 10. Future Improvements

- LLM-powered entity extraction  
- Hybrid chunk + graph retrieval  
- Vector store caching  
- LLM-based router  
- UI dashboard  
- Telemetry / tracing  
- Integration tests and automated evaluation  

---

## 11. Conclusion

This project demonstrates how to combine:

- a knowledge graph  
- embeddings  
- a tool-calling agent  
- multi-step reasoning  

into a single, testable RAG system.

The code is modular, easy to extend, and deliberately structured like a production-ready service.  
The agent is transparent, explainable, and capable of answering multi-hop questions that normal vector search cannot handle.

---

# End of README
