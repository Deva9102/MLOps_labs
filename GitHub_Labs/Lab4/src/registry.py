import json, os
from google.cloud import storage

def _client():
    return storage.Client()

def _bucket():
    name = os.getenv("GCS_BUCKET_NAME")
    if not name:
        raise RuntimeError("GCS_BUCKET_NAME not set")
    return _client().bucket(name)

def read_manifest():
    b = _bucket()
    blob = b.blob("registry/manifest.json")
    if blob.exists(client=_client()):
        return json.loads(blob.download_as_text())
    return {"best_version": 0, "metric": -1.0, "path": ""}

def write_manifest(version: int, metric: float, path: str):
    b = _bucket()
    data = {"best_version": int(version), "metric": float(metric), "path": path}
    b.blob("registry/manifest.json").upload_from_string(json.dumps(data))
