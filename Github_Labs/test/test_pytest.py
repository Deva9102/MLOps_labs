import io
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.train_and_save_model import (
    score_password, compute_batch_metrics, load_passwords,
    ensure_folder_exists, get_model_version, update_model_version,
)

def test_score_password_basics():
    assert score_password("password") <= 10
    assert score_password("A_very_Str0ng!") >= 70
    assert score_password("aaaaaa") < score_password("aaaAAA11!!")

def test_compute_batch_metrics():
    scores = [10, 20, 80, 90]
    m = compute_batch_metrics(scores)
    assert m["count"] == 4
    assert 0 < m["avg_score"] < 100
    assert 0.0 <= m["weak_pct"] <= 1.0
    assert 0.0 <= m["strong_pct"] <= 1.0

def test_load_passwords(tmp_path: Path, monkeypatch):
    csv = tmp_path / "passwords.csv"
    csv.write_text("password\none\ntwo\nthree\n")
    pw = load_passwords(csv, "password")
    assert pw == ["one","two","three"]

def test_gcs_helpers():
    with patch("google.cloud.storage.Client") as MockClient:
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        MockClient.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        mock_blob.exists.return_value = False
        ensure_folder_exists(mock_bucket, "reports")
        mock_bucket.blob.assert_called_with("reports/")
        mock_blob.upload_from_string.assert_called_once_with("")

        # versioning
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = "3"
        assert get_model_version("proj-bkt", "model_version.txt") == 3

        assert update_model_version("proj-bkt", "model_version.txt", 4) is True
