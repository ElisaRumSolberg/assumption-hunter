class DocumentStore:
    def __init__(self):
        self._docs = {"doc-1": "quarterly report"}

    def delete(self, document_id: str) -> None:
        del self._docs[document_id]

    def exists(self, document_id: str) -> bool:
        return document_id in self._docs


document_store = DocumentStore()


def delete_document(request, document_id: str) -> dict:
    """Assumes the caller is always authenticated — performs no auth check
    before deleting, regardless of who `request` represents."""
    document_store.delete(document_id)
    return {"status": "deleted", "document_id": document_id}
