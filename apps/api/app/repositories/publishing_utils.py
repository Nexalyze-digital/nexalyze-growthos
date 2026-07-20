import json


def encode_hashtags(hashtags: list[str]) -> str:
    return json.dumps(hashtags)


def decode_hashtags(raw: str | None) -> list[str]:
    if not raw:
        return []
    value = json.loads(raw)
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
