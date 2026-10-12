import faiss
import numpy as np
import google.generativeai as genai
import os
import pickle
import logging

# Configure Logging
logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self, persistence_dir="data/rag_store", security_manager=None):
        self.dimension = 768 
        self.persistence_dir = persistence_dir
        self.index_file = os.path.join(persistence_dir, "index.faiss")
        self.docs_file = os.path.join(persistence_dir, "docs.pkl")
        self.security = security_manager # Store security manager
        
        # Ensure persistence directory exists
        os.makedirs(persistence_dir, exist_ok=True)
        
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Load existing index if available
        if os.path.exists(self.index_file) and os.path.exists(self.docs_file):
            self.load_index()
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []

    def _embed_content(self, content, task_type, title=None):
        candidate_models = [
            ("models/text-embedding-004", {}),
            ("models/gemini-embedding-001", {"output_dimensionality": self.dimension}),
        ]
        last_err = None
        for model_name, extra_args in candidate_models:
            try:
                kwargs = {
                    "model": model_name,
                    "content": content,
                    "task_type": task_type,
                }
                if title:
                    kwargs["title"] = title
                kwargs.update(extra_args)
                return genai.embed_content(**kwargs)
            except Exception as e:
                last_err = e
                continue
        raise last_err

    def add_memory(self, text):
        """
        Embeds text and adds to Vector DB with persistence.
        """
        try:
            result = self._embed_content(
                content=text,
                task_type="retrieval_document",
                title="Agent Memory"
            )
            vector = np.array(result['embedding']).astype('float32').reshape(1, -1)
            self.index.add(vector)
            self.documents.append(text)
            
            # Auto-save after adding
            self.save_index()
            
        except Exception as e:
            logger.error(f"RAG Error adding memory: {e}")

    def retrieve(self, query, k=2):
        """
        Finds relevant past context for a user query.
        """
        if self.index.ntotal == 0:
            return ""
            
        try:
            result = self._embed_content(
                content=query,
                task_type="retrieval_query"
            )
            query_vector = np.array(result['embedding']).astype('float32').reshape(1, -1)
            distances, indices = self.index.search(query_vector, k)
            
            results = []
            for i in indices[0]:
                if i < len(self.documents) and i >= 0:
                    results.append(self.documents[i])
            return "\n".join(results)
        except Exception as e:
            logger.error(f"RAG Retrieval Error: {e}")
            return ""

    def save_index(self):
        """Saves the FAISS index and documents list to disk (Encrypted)."""
        try:
            faiss.write_index(self.index, self.index_file)
            
            # Serialize docs
            docs_bytes = pickle.dumps(self.documents)
            
            # Encrypt if security manager is present
            if self.security:
                data_to_write = self.security.encrypt_data(docs_bytes)
            else:
                data_to_write = docs_bytes
                
            with open(self.docs_file, "wb") as f:
                f.write(data_to_write)
        except Exception as e:
            logger.error(f"Failed to save RAG index: {e}")

    def load_index(self):
        """Loads the FAISS index and documents list from disk (Decrypted)."""
        try:
            self.index = faiss.read_index(self.index_file)
            
            with open(self.docs_file, "rb") as f:
                data_read = f.read()
                
            # Decrypt if security manager is present
            if self.security:
                try:
                    decrypted_data = self.security.decrypt_data(data_read)
                    self.documents = pickle.loads(decrypted_data)
                except:
                    # Fallback: maybe it wasn't encrypted before?
                    self.documents = pickle.loads(data_read)
            else:
                self.documents = pickle.loads(data_read)
                
            logger.info(f"Loaded RAG index with {len(self.documents)} documents.")
        except Exception as e:
            logger.error(f"Failed to load RAG index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []