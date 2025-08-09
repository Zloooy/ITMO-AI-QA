import json
import requests
import time
from jwcrypto import jwk, jws
import sys


def get_iam(secrets_file):
    # Чтение закрытого ключа из JSON-файла
    with open(secrets_file, "r") as f:
        obj = f.read()
        obj = json.loads(obj)
        private_key_pem = obj["private_key"]
        key_id = obj["id"]
        service_account_id = obj["service_account_id"]

    # Load the private key using jwcrypto
    private_key = jwk.JWK.from_pem(private_key_pem.encode("utf-8"))

    now = int(time.time())
    payload = {
        "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        "iss": service_account_id,
        "iat": now,
        "exp": now + 3600,
    }

    # Формирование JWT с использованием jwcrypto
    header = {"alg": "PS256", "typ": "JWT", "kid": key_id}

    signer = jws.JWS(json.dumps(payload).encode("utf-8"))
    signer.add_signature(private_key, None, json.dumps(header))
    encoded_token = signer.serialize(compact=True)

    headers = {
        "Content-Type": "application/json",
    }

    json_data = {
        "jwt": encoded_token,
    }

    iam_token = requests.post(
        "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        headers=headers,
        json=json_data,
    ).json()["iamToken"]
    return iam_token
