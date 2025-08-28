from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from app.core.config import settings

def analyze_document(blob_url: str):
    client = DocumentAnalysisClient(
        endpoint=settings.AZURE_FORM_RECOGNIZER_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_FORM_RECOGNIZER_KEY)
    )
    poller = client.begin_analyze_document_from_url("prebuilt-document", blob_url)
    result = poller.result()

    # Extract text / summary
    raw_json = [r.to_dict() for r in result.pages]
    # summary_text = " ".join([p.content for p in result.pages])
    # confidence_score = 1.0  # placeholder if needed
    return raw_json
