import os
import logging
import logging
from typing import List, Dict, Tuple

from chatbot_v3.src.tool_orchestrator import ToolOrchestrator

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EvaluatorAgent:
    def evaluate_context(self, context: str) -> bool:
        """
        Evaluates the quality and relevance of the context.
        Currently checks if the context contains results from at least two different sources
        (Vector Store, PubMed, and Web Search).
        """
        has_vector_store = "Vector Store Results:" in context
        has_pubmed = "PubMed Results:" in context
        has_web_search = "Web Search Results:" in context

        return sum([has_vector_store, has_pubmed, has_web_search]) >= 2

class FinishingAgent:
    def synthesize_response(self, context: str) -> str:
        """
        Synthesizes a final response based on the aggregated context.
        For this initial implementation, concatenates the context string
        with a brief introductory phrase.
        """
        synthesized_response = "Here's a comprehensive summary of the information gathered: " + context
        return synthesized_response

class CentralAgent:
    def __init__(self):
        # Initialize the Central Agent
        self.orchestrator = ToolOrchestrator()
        self.evaluator = EvaluatorAgent()
        self.finisher = FinishingAgent()
        logging.info("CentralAgent initialized.")

    def process_query(self, query: str) -> Tuple[str, list]:
        """Processes the user query and returns a response along with sources."""
        tools = ["VectorStore", "PubMed", "WebSearch"]
        # execute_tools returns an aggregated string of results
        response_string = self.orchestrator.execute_tools(tools, query)
        # Source information is not directly available from the aggregated string
        # Returning the string directly and an empty list for sources
        sources = []
        return response_string, sources

    def recognize_intent(self, query: str) -> str:
        # Placeholder for intent recognition logic
        logging.debug(f"Recognizing intent for query: {query}")
        return "information_retrieval"

    def select_tools(self, intent: str) -> List[str]:
        # Placeholder for tool selection logic
        logging.debug(f"Selecting tools for intent: {intent}")
        if intent == "information_retrieval":
            return ["VectorStore", "PubMed", "WebSearch"]
        else:
            return []

if __name__ == "__main__":
    agent = CentralAgent()
    response, sources = agent.process_query("Alzheimer's disease treatments")
    print(response)
    print(sources)