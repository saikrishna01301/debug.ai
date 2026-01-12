from dotenv import load_dotenv
from app.services.vector_store import VectorStore

# Load environment variables
load_dotenv()


def test_vector_store():
    print("=" * 60)
    print("Testing Vector Store")
    print("=" * 60)

    # Initialize
    vs = VectorStore()

    # Test 1: Add a single document
    print("\nTest 1: Adding single document...")
    vs.add_document(
        text="KeyError occurs when trying to access a dictionary key that doesn't exist. Use dict.get() or check if key exists first.",
        metadata={
            "source": "stackoverflow",
            "language": "python",
            "tags": "python,dictionary,keyerror",
        },
        doc_id="test_doc_1",
    )
    print("✓ Document added")

    # Test 2: Add multiple documents
    print("\nTest 2: Adding batch of documents...")
    texts = [
        "TypeError happens when you perform an operation on incompatible types. For example, adding a string and integer.",
        "Cannot read property 'map' of undefined in React usually means your data hasn't loaded yet. Use conditional rendering.",
        "ModuleNotFoundError means Python can't find the module you're trying to import. Check your pip install and PYTHONPATH.",
    ]

    metadatas = [
        {
            "source": "stackoverflow",
            "language": "python",
            "tags": "python,typeerror",
        },
        {
            "source": "stackoverflow",
            "language": "javascript",
            "tags": "react,javascript",
        },
        {"source": "stackoverflow", "language": "python", "tags": "python,import"},
    ]

    ids = ["test_doc_2", "test_doc_3", "test_doc_4"]

    vs.add_documents_batch(texts, metadatas, ids)

    # Test 3: Search
    print("\nTest 3: Searching...")
    print("\nQuery: 'dictionary key not found error'")
    results = vs.search("dictionary key not found error", n_results=3)

    print(f"\nFound {len(results['documents'][0])} results:")
    for i, (doc, meta, distance) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ):
        print(f"\n--- Result {i+1} (distance: {distance:.4f}) ---")
        print(f"Language: {meta['language']}")
        print(f"Tags: {meta['tags']}")
        print(f"Content: {doc[:100]}...")

    # Test 4: Search with filter
    print("\n" + "=" * 60)
    print("Test 4: Searching with filter (Python only)")
    print("=" * 60)
    results_filtered = vs.search(
        "error with undefined value",
        n_results=3,
        filter_metadata={"language": "python"},
    )

    print(f"\nFound {len(results_filtered['documents'][0])} Python results:")
    for i, (doc, meta) in enumerate(
        zip(results_filtered["documents"][0], results_filtered["metadatas"][0])
    ):
        print(f"\n--- Result {i+1} ---")
        print(f"Language: {meta['language']}")
        print(f"Content: {doc[:100]}...")

    # Stats
    print("\n" + "=" * 60)
    stats = vs.get_stats()
    print(f"Total documents in database: {stats['total_documents']}")
    print(f"Collection name: {stats['collection_name']}")


if __name__ == "__main__":
    test_vector_store()
