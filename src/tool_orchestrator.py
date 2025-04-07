import chromadb
import os
import logging
from typing import List
from Bio import Entrez
import requests

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ENTREZ_EMAIL = os.getenv("ENTREZ_EMAIL")
if not ENTREZ_EMAIL:
    raise ValueError("ENTREZ_EMAIL environment variable not set.")
Entrez.email = ENTREZ_EMAIL

class ToolOrchestrator:
    def __init__(self):
        # Initialize the Tool Orchestrator
        try:
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection("my_collection")
            # Add some sample data
            self.collection.add(
                documents=[
                    "Alzheimer's disease is a progressive neurodegenerative disorder.",
                    "New treatments for Alzheimer's are being developed.",
                    "Early diagnosis is crucial for managing Alzheimer's disease."
                ],
                ids=["doc1", "doc2", "doc3"]
            )
            logging.info("ToolOrchestrator initialized successfully with ChromaDB connection and sample data.")
        except Exception as e:
            logging.error(f"Error initializing ToolOrchestrator: {e}")
            # Depending on the desired behavior, you might want to raise the exception
            # or handle it in a way that allows the application to continue (if possible)
            # For now, we log the error and the object might be in a partially initialized state.
            self.client = None
            self.collection = None

    def execute_tools(self, tools: list, query: str) -> str:
        # Execute the selected tools and aggregate the results
        results = []
        logging.info(f"Executing tools: {tools} for query: '{query}'")
        for tool in tools:
            try:
                if tool == "VectorStore":
                    tool_result_dict = self.query_vector_store(query)
                    # Extract content string before appending
                    results.append(tool_result_dict.get("contents", ["Vector Store Error"])[0])
                    logging.info(f"Successfully executed tool: {tool}")
                elif tool == "PubMed":
                    tool_result_dict = self.query_pubmed(query)
                    # Extract content string before appending
                    results.append(tool_result_dict.get("contents", ["PubMed Error"])[0])
                    logging.info(f"Successfully executed tool: {tool}")
                elif tool == "WebSearch":
                    tool_result_dict = self.perform_web_search(query)
                    # Extract content string before appending
                    results.append(tool_result_dict.get("contents", ["Web Search Error"])[0])
                    logging.info(f"Successfully executed tool: {tool}")
                else:
                    logging.warning(f"Unknown tool requested: {tool}")
                    results.append(f"Unknown tool: {tool}")
            except Exception as e:
                logging.error(f"Error executing tool {tool}: {e}")
                results.append(f"Error executing {tool}: {e}")

        logging.info("Finished executing all requested tools.")
        return "\n".join(results)

    def query_vector_store(self, query: str) -> dict:
        # Query the vector store
        logging.debug(f"Querying Vector Store with: '{query}'")
        if not self.collection:
            logging.error("Vector store collection is not initialized.")
            return {"contents": ["Vector Store Error: Collection not initialized."], "sources": []}
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=2
            )
            logging.info(f"Vector Store query successful for: '{query}'")
            return {"contents": [doc.page_content for doc in results["documents"][0]], "sources": [doc.metadata.get("source", "unknown") for doc in results["documents"][0]]}
        except Exception as e:
            logging.error(f"Error querying Vector Store: {e}")
            return {"contents": [f"Vector Store Query Error: {e}"], "sources": []}

    def query_pubmed(self, query: str) -> dict:
        # Query PubMed
        logging.debug(f"Querying PubMed with: '{query}'")
        try:
            handle = Entrez.esearch(db="pubmed", term=query, retmax=5, rettype="abstract", retmode="xml")
            record = Entrez.read(handle)
            handle.close()

            results = []
            id_list = record.get("IdList", [])
            if not id_list:
                logging.warning(f"No PubMed results found for query: '{query}'")
                return {"contents": ["PubMed Results:\nNo results found."], "sources": []}

            logging.info(f"Found {len(id_list)} PubMed IDs for query: '{query}'")
            for pubmed_id in id_list:
                try:
                    fetch_handle = Entrez.efetch(db="pubmed", id=pubmed_id, rettype="abstract", retmode="xml")
                    article = Entrez.read(fetch_handle)
                    fetch_handle.close()
                    # Safely access nested dictionary keys
                    medline_citation = article.get("MedlineCitation", {})
                    article_info = medline_citation.get("Article", {})
                    title = article_info.get("ArticleTitle", "No Title Available")
                    abstract_info = article_info.get("Abstract", {})
                    abstract = abstract_info.get("AbstractText", ["No Abstract Available"])[0] # Get first abstract text if available
                    results.append(f"Title: {title}\nAbstract: {abstract}\n")
                    logging.debug(f"Fetched details for PubMed ID: {pubmed_id}")
                except Exception as fetch_e:
                    logging.error(f"Error fetching details for PubMed ID {pubmed_id}: {fetch_e}")
                    results.append(f"Error fetching details for ID {pubmed_id}")

            logging.info(f"PubMed query successful for: '{query}'")
            return {"contents": ["PubMed Results:\n" + "\n".join(results)], "sources": [pubmed_id for pubmed_id in id_list]}
        except Exception as e:
            logging.error(f"Error querying PubMed: {e}")
            # Return a more specific error message if possible
            return {"contents": [f"PubMed Query Error: {type(e).__name__} - {e}"], "sources": []}

    def perform_web_search(self, query: str) -> dict:
        # Perform a web search using DuckDuckGo (Example - might be blocked)
        # Note: Scraping search engines directly can be unreliable and against terms of service.
        # Consider using a dedicated search API (e.g., Google Custom Search, Bing Search API) for production.
        logging.debug(f"Performing web search for: '{query}'")
        try:
            # Using a simple GET request to DuckDuckGo HTML endpoint.
            # This is NOT a reliable method for production.
            url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers, timeout=10) # Added timeout
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            # Basic parsing attempt - this is fragile
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('div', class_='result__body')
            snippets = [f"{res.find('a', class_='result__a').text}\n{res.find('a', class_='result__snippet').text}\n" for res in search_results[:3]] # Get top 3 results

            if not snippets:
                 logging.warning(f"No web search results found or parsed for query: '{query}'")
                 return {"contents": ["Web Search Results:\nNo results found."], "sources": []}

            logging.info(f"Web search successful for: '{query}'")
            return {"contents": ["Web Search Results:\n" + "\n".join(snippets)], "sources": [result["url"] for result in [{"title": "Example Webpage", "snippet": "Example snippet", "url": "https://example.com"}]]}
        except requests.exceptions.RequestException as e:
            logging.error(f"Web Search Request Error: {e}")
            return {"contents": [f"Web Search Error: {e}"], "sources": []}
        except Exception as e:
            logging.error(f"Error during web search processing: {e}")
            return {"contents": [f"Web Search Processing Error: {e}"], "sources": []}

if __name__ == "__main__":
    orchestrator = ToolOrchestrator()
    if orchestrator.collection: # Check if initialization was successful
        tools = ["VectorStore", "PubMed", "WebSearch", "UnknownTool"]
        query = "Alzheimer's disease treatments"
        results = orchestrator.execute_tools(tools, query)
        print(results)
    else:
        print("Tool Orchestrator failed to initialize.")