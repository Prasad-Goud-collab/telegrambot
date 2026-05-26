# src/groupbot/vectorstore/faiss_store.py

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import pandas as pd


SIMILARITY_THRESHOLD = 0.75


class QAVectorStore:
    """
    Builds FAISS vectorstore from verified Q&A CSV.
    Performs semantic similarity search on user questions.
    """

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None

    def build_from_csv(self, csv_path: str) -> None:
        """
        Loads verified Q&A CSV and builds FAISS vectorstore.

        Args:
            csv_path (str): Path to verified_qa.csv
        """
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["question", "answer"])
        df = df.reset_index(drop=True)

        if df.empty:
            raise RuntimeError("CSV is empty. Add Q&A pairs first.")

        # Build documents — embed questions, store answers in metadata
        documents = []
        for _, row in df.iterrows():
            doc = Document(
                page_content=row["question"],
                metadata={
                    "answer": row["answer"],
                    "category": row.get("category", "General"),
                    "answered_by": row.get("answered_by", "unknown"),
                    "original_question": row["question"]
                }
            )
            documents.append(doc)

        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        print(f"✅ FAISS built with {len(documents)} verified Q&A pairs.")

    def search(self, query: str, threshold: float = SIMILARITY_THRESHOLD) -> dict:
        """
        Searches for semantically similar verified question.

        Args:
            query (str): Incoming user question
            threshold (float): Minimum similarity score

        Returns:
            dict: result with found, answer, confidence, matched_question
        """
        if not self.vectorstore:
            raise RuntimeError("Vectorstore not built. Call build_from_csv first.")

        # Get top match with similarity score
        results = self.vectorstore.similarity_search_with_score(query, k=1)

        if not results:
            return {
                "found": False,
                "answer": None,
                "confidence": 0.0,
                "matched_question": None,
                "category": None,
                "answered_by": None
            }

        doc, score = results[0]

        # Convert L2 distance to similarity (0 to 1)
        similarity = float(1 / (1 + score))

        if similarity >= threshold:
            return {
                "found": True,
                "answer": doc.metadata["answer"],
                "confidence": round(similarity, 4),
                "matched_question": doc.metadata["original_question"],
                "category": doc.metadata["category"],
                "answered_by": doc.metadata["answered_by"]
            }
        else:
            return {
                "found": False,
                "answer": None,
                "confidence": round(similarity, 4),
                "matched_question": doc.metadata["original_question"],
                "category": None,
                "answered_by": None
            }

    def add_new_qa(self, question: str, answer: str,
                   category: str = "General",
                   answered_by: str = "user") -> None:
        """
        Adds new Q&A pair to existing FAISS index in real-time.
        No need to rebuild entire index.

        Args:
            question (str): New verified question
            answer (str): Verified answer
        """
        doc = Document(
            page_content=question,
            metadata={
                "answer": answer,
                "category": category,
                "answered_by": answered_by,
                "original_question": question
            }
        )

        if self.vectorstore:
            # ✅ Add to existing index without rebuilding
            self.vectorstore.add_documents([doc])
            print(f"✅ New Q&A added to FAISS: {question[:50]}...")
        else:
            raise RuntimeError("Vectorstore not built yet.")

    def is_ready(self) -> bool:
        return self.vectorstore is not None