"""
RAGAgent is a class that combines a LLaMA model with a vector store index
to generate text based on user input.

The class uses the llama_index library to create a vector store index from
a directory of text files, and the LLaMA model to generate text based on user
input.

The class has methods for loading a persisted index, updating the index with
new documents, and querying the index with user input.

The class also has methods for generating text based on the output of the
query engine.

"""

import os
import hashlib
import json
import re

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage,
    set_global_tokenizer,
)
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.llms.llama_cpp.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.memory import ChatMemoryBuffer
from transformers import AutoTokenizer
from dataclasses import dataclass


@dataclass
class Reference:
    text: str
    page: int
    title: str


class RAGAgent:
    """
    Initialize the RAGAgent class.

    Args:
        llm_url (str): The URL of the LLaMA model.
        directory (str): The directory containing the text files to index.
        agent_types (list[str]): The types of agents to support. Defaults to
            ["philosopher", "lawyer", "monk", "productivity"].
    """

    def __init__(
        self,
        llm_url: str = "https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf",
        directory: str = "../holy_texts",
        agent_types: list[str] = ["monk"],
    ):
        # Load the LLaMA model
        self.llm = LlamaCPP(
            model_url=llm_url,
            temperature=0.4,
            max_new_tokens=1000,
            context_window=64000,
            model_kwargs={"n_gpu_layers": -1},  # Set to at least 1 to use GPU
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt,
            generate_kwargs={
                "stop": ["/SYS", "[/INST]", "</INST>", "[[INST]]"]
            },  # Add this line
            verbose=True,
        )
        Settings.llm = self.llm
        set_global_tokenizer(
            AutoTokenizer.from_pretrained(
                "meta-llama/Meta-Llama-3.1-8B-Instruct"
            ).encode
        )

        # Load the agent types
        self.agent_types = agent_types

        # Set the embedding model
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

        # Initialize the index
        self.indices = {}
        for agent in agent_types:
            self.indices[agent], previous_hashes = self._load_or_create_index(
                directory + f"/{agent}", f"storage/{agent}"
            )
            self.indices[agent] = self._update_index(
                self.indices[agent],
                directory + f"/{agent}",
                previous_hashes,
                f"storage/{agent}",
            )
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

    def _get_document_hashes(self, directory):
        """
        Get the document hashes for a given directory.

        Args:
            directory (str): The directory to get the document hashes for.

        Returns:
            dict: A dictionary of document hashes, where the keys are the file
                paths and the values are the hashes.
        """
        document_hashes = {}
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                document_hashes[file_path] = file_hash
        return document_hashes

    def _load_or_create_index(
        self, directory, persist_dir="storage"
    ) -> tuple[VectorStoreIndex, dict]:
        """
        Load a persisted index or create a new one.

        Args:
            directory (str): The directory to load the index from.
            persist_dir (str): The directory to persist the index to. Defaults
                to "storage".

        Returns:
            tuple: A tuple containing the index and the previous document hashes.
        """
        # Check if we have a persisted index
        if os.path.exists(persist_dir):
            print("Loading existing index...")
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)

            # Load the previous document hashes
            with open(os.path.join(persist_dir, "document_hashes.json"), "r") as f:
                previous_hashes = json.load(f)
        else:
            print("Creating new index...")
            documents = SimpleDirectoryReader(directory, recursive=True).load_data()
            index = VectorStoreIndex.from_documents(documents, show_progress=True)

            os.makedirs(persist_dir)
            # Save the initial document hashes
            previous_hashes = self._get_document_hashes(directory)
            with open(os.path.join(persist_dir, "document_hashes.json"), "w") as f:
                json.dump(previous_hashes, f)

            index.storage_context.persist(persist_dir=persist_dir)

        return index, previous_hashes

    def _update_index(
        self,
        index: VectorStoreIndex,
        directory: str,
        previous_hashes: dict,
        persist_dir: str,
    ) -> VectorStoreIndex:
        """
        Update the index with new or modified documents.

        Args:
            index (VectorStoreIndex): The index to update.
            directory (str): The directory to update the index from.
            previous_hashes (dict): The previous document hashes.
            persist_dir (str): The directory to persist the index to.

        Returns:
            VectorStoreIndex: The updated index.
        """
        current_hashes = self._get_document_hashes(directory)

        # Check for new or modified documents
        updated_docs = []
        for file_path, current_hash in current_hashes.items():
            if (
                file_path not in previous_hashes
                or previous_hashes[file_path] != current_hash
            ):
                print(f"Updating document: {file_path}")
                doc = SimpleDirectoryReader(input_files=[file_path]).load_data()[0]
                updated_docs.append(doc)

        # Check for deleted documents
        for file_path in previous_hashes:
            if file_path not in current_hashes:
                print(f"Removing document: {file_path}")
                index.delete(file_path)

        # Update the index with new or modified documents
        if updated_docs:
            index.refresh(updated_docs)

        # Persist the updated index and document hashes
        index.storage_context.persist(persist_dir=persist_dir)
        with open(os.path.join(persist_dir, "document_hashes.json"), "w") as f:
            json.dump(current_hashes, f)

        return index

    def query(self, query: str, agent_type: str, stream: bool = False) -> str:
        """
        Query the index with user input and generate text based on the output.

        Args:
            query (str): The user input to query the index with.
            agent_type (str): The type of agent to use for generating text.

        Returns:
            str: The generated text.
        """
        if agent_type not in self.agent_types:
            raise ValueError(f"Invalid agent type: {agent_type}")

        # Set up advanced retrieval
        vector_retriever = VectorIndexRetriever(
            index=self.indices[agent_type], similarity_top_k=10
        )

        # Create the query engine
        query_engine = RetrieverQueryEngine.from_args(
            streaming=stream, retriever=vector_retriever, verbose=False
        )

        with open("promptfile.json", "r") as file:
            prompts = json.load(file)

        query = prompts[agent_type] + "\n Here is the new query from the user: " + query

        response = query_engine.query(query)
        references = []
        for node in response.source_nodes:
            r = {
                "text": node.node.text[:200].lstrip("0123456789"),
                "page": node.node.metadata["page_label"],
                "title": node.node.metadata["file_name"],
            }

            references.append(r)

        if stream:
            print("Response:", response.print_response_stream())
        else:
            return {
                "response": re.sub(r"[\[\]\{\}<>]", "", str(response)[8:]).rstrip(
                    "SYS"
                ),
                "references": references,
            }

        print("\n" + "=" * 60 + "\n")
        print("References:")
        # Access source nodes and their metadata
        for node in response.source_nodes:
            print(
                f"Source text: {node.node.text[:200].lstrip('0123456789')}..."
            )  # First 50 characters of the source text
            if "page_label" in node.node.metadata:
                print(f"Page number: {node.node.metadata['page_label']}")
            if "file_name" in node.node.metadata:
                print(f"Filename: {node.node.metadata['file_name']}")
            print("--------------------------------------------")
        print("\n" + "=" * 60 + "\n")

        return response
