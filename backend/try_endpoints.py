"""
try_endpoints.py

Simple endpoint tester for the Meridian FastAPI backend.

Start the API first:
    uvicorn api.main:app --reload

Then run:
    python try_endpoints.py

Or:
    uv run python try_endpoints.py
"""

import sys
from pathlib import Path

import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "http://127.0.0.1:8001"

# Change this to a real PDF on your computer.
PDF_FILE = Path(__file__).resolve().parent.parent / "uploads" / "aldermoor_annual_report_fy2024.pdf"

TIMEOUT = 120


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_header(title: str):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_response(response: requests.Response):
    print(f"HTTP {response.status_code}")

    try:
        print(response.json())
    except ValueError:
        print(response.text)


def check_server():
    """Make sure the FastAPI server is running."""
    print_header("SERVER CHECK")

    try:
        response = requests.get(
            f"{BASE_URL}/api/health",
            timeout=10,
        )

        print_response(response)

        if response.ok:
            print("\nServer is reachable.")
            return True

        print("\nServer returned an error.")
        return False

    except requests.exceptions.ConnectionError:
        print(
            f"\nCould not connect to {BASE_URL}\n"
            "Make sure FastAPI is running."
        )
        return False

    except Exception as exc:
        print(f"\nUnexpected error: {exc}")
        return False


# ---------------------------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------------------------

def test_health():
    print_header("1. GET /api/health")

    response = requests.get(
        f"{BASE_URL}/api/health",
        timeout=TIMEOUT,
    )

    print_response(response)


# ---------------------------------------------------------------------------
# GET /api/status
# ---------------------------------------------------------------------------

def test_status():
    print_header("2. GET /api/status")

    response = requests.get(
        f"{BASE_URL}/api/status",
        timeout=TIMEOUT,
    )

    print_response(response)


# ---------------------------------------------------------------------------
# POST /api/rag/ask
# ---------------------------------------------------------------------------

def test_rag_ask():
    print_header("3. POST /api/rag/ask")

    payload = {
        "query": "What are the procurement requirements?",
        "retriever_type": "similarity",
    }

    print("Request:")
    print(payload)

    response = requests.post(
        f"{BASE_URL}/api/rag/ask",
        json=payload,
        timeout=TIMEOUT,
    )

    print("\nResponse:")
    print_response(response)


# ---------------------------------------------------------------------------
# POST /api/agent/audit
# ---------------------------------------------------------------------------

def test_agent_audit():
    print_header("4. POST /api/agent/audit")

    payload = {
        "request_text": (
            "Review this procurement request and identify "
            "compliance, financial, and policy risks."
        )
    }

    print("Request:")
    print(payload)

    response = requests.post(
        f"{BASE_URL}/api/agent/audit",
        json=payload,
        timeout=TIMEOUT,
    )

    print("\nResponse:")
    print_response(response)


# ---------------------------------------------------------------------------
# POST /api/rag/upload
# ---------------------------------------------------------------------------

def test_upload():
    print_header("5. POST /api/rag/upload")

    if not PDF_FILE.exists():
        print(f"PDF not found: {PDF_FILE}")
        print()
        print("Update PDF_FILE at the top of this script.")
        print("Example:")
        print('    PDF_FILE = Path("data/my_document.pdf")')
        return

    print(f"Uploading: {PDF_FILE}")

    try:
        with PDF_FILE.open("rb") as pdf:
            files = [
                (
                    "files",
                    (
                        PDF_FILE.name,
                        pdf,
                        "application/pdf",
                    ),
                )
            ]

            response = requests.post(
                f"{BASE_URL}/api/rag/upload",
                files=files,
                timeout=TIMEOUT,
            )

        print("\nResponse:")
        print_response(response)

    except Exception as exc:
        print(f"Upload failed: {exc}")


# ---------------------------------------------------------------------------
# POST /api/rag/upload with multiple files
# ---------------------------------------------------------------------------

def test_multiple_upload():
    print_header("6. POST /api/rag/upload - Multiple Files")

    pdf_files = list(Path("data").glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in the data/ folder.")
        return

    print("Files:")
    for pdf in pdf_files:
        print(f"  - {pdf}")

    opened_files = []

    try:
        multipart_files = []

        for pdf in pdf_files:
            file_handle = pdf.open("rb")
            opened_files.append(file_handle)

            multipart_files.append(
                (
                    "files",
                    (
                        pdf.name,
                        file_handle,
                        "application/pdf",
                    ),
                )
            )

        response = requests.post(
            f"{BASE_URL}/api/rag/upload",
            files=multipart_files,
            timeout=TIMEOUT,
        )

        print("\nResponse:")
        print_response(response)

    except Exception as exc:
        print(f"Multiple upload failed: {exc}")

    finally:
        for file_handle in opened_files:
            file_handle.close()


# ---------------------------------------------------------------------------
# GET /api/rag/uploads
# ---------------------------------------------------------------------------

def test_upload_history():
    print_header("7. GET /api/rag/uploads")

    response = requests.get(
        f"{BASE_URL}/api/rag/uploads",
        timeout=TIMEOUT,
    )

    print_response(response)


# ---------------------------------------------------------------------------
# POST /api/rag/ingest
# ---------------------------------------------------------------------------

def test_ingest():
    print_header("8. POST /api/rag/ingest")

    response = requests.post(
        f"{BASE_URL}/api/rag/ingest",
        timeout=TIMEOUT,
    )

    print_response(response)


# ---------------------------------------------------------------------------
# POST /api/rag/ingest-gcs
# ---------------------------------------------------------------------------

def test_ingest_gcs_legacy():
    print_header("9. POST /api/rag/ingest-gcs (legacy route)")

    response = requests.post(
        f"{BASE_URL}/api/rag/ingest-gcs",
        timeout=TIMEOUT,
    )

    print_response(response)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("=" * 70)
    print("MERIDIAN API ENDPOINT TESTER")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")

    # First verify that the server is running.
    if not check_server():
        sys.exit(1)

    # Basic endpoints
    test_health()
    test_status()

    # RAG
    test_rag_ask()

    # Agent
    test_agent_audit()

    # Upload
    test_upload()

    # Multiple upload
    # Comment this out if you don't want to upload every PDF in data/.
    test_multiple_upload()

    # Upload history
    test_upload_history()

    # Stored-document ingestion
    test_ingest()

    # Legacy endpoint
    test_ingest_gcs_legacy()

    print_header("TESTING COMPLETE")


if __name__ == "__main__":
    main()
