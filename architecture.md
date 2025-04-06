graph TD
    User[User] --> UI[Web Interface]
    UI --> Central[Central AI Agent]

    Central --> ToolOrch[Tool Orchestrator]
    ToolOrch --> VectorStore[Vector Store Manager]
    ToolOrch --> PubMed[PubMed Connector]
    ToolOrch --> WebSearch[Web Search Connector]
    ToolOrch --> StructuredDB[Structured Database Connector]
    ToolOrch --> ModelKnowledge[Model Knowledge]

    VectorStore --> ContextAgg[Context Aggregator]
    PubMed --> ContextAgg
    WebSearch --> ContextAgg
    StructuredDB --> ContextAgg
    ModelKnowledge --> ContextAgg

    ContextAgg --> Evaluator[Evaluator Agent]
    Evaluator --> Central

    Evaluator --> Finisher[Finishing Agent]
    Finisher --> UI

    subgraph Document Management
        DocUpload[Document Upload] --> VectorStore
        VectorStoreAdmin[Vector Store Admin] --> VectorStore
    end

    style Central fill:#f9f,stroke:#333,stroke-width:2px
    style Evaluator fill:#ccf,stroke:#333,stroke-width:2px
    style Finisher fill:#fcf,stroke:#333,stroke-width:2px

    linkStyle 0,1 stroke:#333,stroke-width:1px
    linkStyle 2,3,4,5,6 stroke:#333,stroke-width:1px
    linkStyle 7,8,9,10 stroke:#333,stroke-width:1px
    linkStyle 11 stroke:#333,stroke-width:1px
    linkStyle 12 stroke:#333,stroke-width:1px