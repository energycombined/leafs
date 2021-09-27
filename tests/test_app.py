import shutil
from pathlib import Path
import os
import gzip

import pytest
from leafspy import flask_server
from flask import jsonify
from werkzeug.datastructures import FileStorage


@pytest.fixture
def client():
    """Flask app client"""
    return flask_server.app.test_client()


def test_import(client):
    pass


def test_base_route_that_does_not_exist(client):
    url = '/'
    response = client.get(url)
    assert response.get_data() == b'This page does not exist'
    assert response.status_code == 404


def test_upload_file_get(client):
    url = '/upload_file'

    response = client.get(url)
    assert b"Upload" in response.get_data()
    assert response.status_code == 200


def test_upload_file_post_no_file(client):
    url = '/upload_file'
    message = {
        "test_type": "some-test",
        "test_type_subcategory": "details",
        "instrument": "tester",
        "instrument_brand": "audi",
    }

    response = client.post(url, data=message)
    j = response.get_json()

    assert j["Code"] == 1
    assert j["Message"] == "No file attached"
    assert response.status_code == 200


def test_upload_file_post_arbin(client, tmp_path):
    arbin_test_file = "546_ES_Fe02CDvsNi_HalleMix_Repro.res"
    arbin_file_path = Path("../test_data") / arbin_test_file
    temp_gz_file_path = tmp_path / "arbin_test_file.res.gz"
    assert arbin_file_path.is_file()

    with open(arbin_file_path, "rb") as f_in:
        with gzip.open(temp_gz_file_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    arbin_file = FileStorage(
        stream=open(temp_gz_file_path, "rb"),
        filename="arbin_test_file.res.gz",
    )

    url = '/upload_file'
    data = {
        "test_type": "CHARGE-DISCHARGE",
        "test_type_subcategory": "GALVANOSTATIC CYCLING",
        "instrument": "BT-2000",
        "instrument_brand": "ARBIN",
        "files": arbin_file,
    }

    response = client.post(url, data=data, content_type="multipart/form-data")
    payload = response.get_json()
    assert "experiment_data" in payload.keys()
    assert "experiment_info" in payload.keys()
    assert response.status_code == 200
