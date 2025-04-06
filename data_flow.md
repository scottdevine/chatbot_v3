## RAG Chatbot Data Flow

This document details the flow of a user query through the RAG chatbot system.

**1. User Query:**

*   The user submits a query through the Web Interface (UI).

**2. Central AI Agent Analysis:**

*   The Central AI Agent receives the query and performs the following:
    *   **Intent Recognition:** Determines the user's intent.
    *   **Query Decomposition:** Breaks down complex queries into smaller, manageable steps.
    *   **Tool Selection:** Identifies the appropriate tools needed to fulfill the query.

**3. Tool Orchestration:**

*   The Tool Orchestrator receives the tool requests from the Central AI Agent and executes them in parallel or sequentially, as determined by the agent.

**4. Data Retrieval:**

*   The selected tools retrieve data from various sources:
    *   **Vector Store Manager:** Retrieves relevant documents from the vector store.
    *   **PubMed Connector:** Queries medical literature.
    *   **Web Search Connector:** Performs web searches.
    *   **Structured Database Connector:** Queries structured databases.
    *   **Model Knowledge:** Accesses the LLM's internal knowledge.

**5. Context Aggregation:**

*   The Context Aggregator receives the results from all tools, removes duplicates, ranks the results by relevance, and combines them into a unified context.

**6. Evaluation:**

*   The Evaluator Agent assesses the quality and sufficiency of the aggregated context.
*   If the context is insufficient, it requests additional information from the Central AI Agent, triggering another round of tool execution.

**7. Response Generation:**

*   Once the context is deemed sufficient, the Finishing Agent synthesizes a final response, incorporating citations to the source materials.

**8. UI Display:**

*   The final response is displayed to the user through the Web Interface (UI).