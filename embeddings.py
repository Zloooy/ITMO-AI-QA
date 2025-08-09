from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import IAMTokenAuth
from config import YANDEX_FOLDER_ID, YGPT_SERVICE_ACCOUNT_KEY_FILE_CREDENTIALS
from utils import get_iam

sdk = YCloudML(
    folder_id=YANDEX_FOLDER_ID,
    auth=IAMTokenAuth(get_iam(YGPT_SERVICE_ACCOUNT_KEY_FILE_CREDENTIALS)),
)
doc_model = sdk.models.text_embeddings("doc")
query_model = sdk.models.text_embeddings("query")


def encode_document(text: str):
    return doc_model.embed_text(text)


def encode_query(text: str):
    return query_model.embed_text(text)
