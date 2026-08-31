import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.documents import delete_document, document_store


class AnonymousRequest:
    """Represents a caller with no authentication token or session."""

    user = None


def test_delete_document_succeeds_for_unauthenticated_caller():
    """Demonstrates the bug: an anonymous caller can delete a document.

    A correct implementation would reject this with a 401/403-style error.
    Instead delete_document performs the deletion unconditionally, which is
    exactly the failure the hidden 'caller is always authenticated' assumption
    predicts.
    """
    assert document_store.exists("doc-1")

    result = delete_document(request=AnonymousRequest(), document_id="doc-1")

    assert result["status"] == "deleted"
    assert not document_store.exists("doc-1")
