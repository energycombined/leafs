"""Tests for leafspy"""

import gzip
import shutil
from pathlib import Path
from flaskr import flaskr
import tempfile

import pytest
from werkzeug.datastructures import FileStorage

from leafspy import flask_server

FIXTURE_DIR = Path(__file__).parents[1].resolve() / "test_data"


@pytest.fixture

def client():
    db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    flaskr.app.config['TESTING'] = True

    with flaskr.app.test_client() as client:
        with flaskr.app.app_context():
            flaskr.init_db()
        yield client

    os.close(db_fd)
    os.unlink(flaskr.app.config['DATABASE'])

def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'No entries here so far' in rv.data

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
    arbin_file_path = FIXTURE_DIR / arbin_test_file
    temp_gz_file_path = tmp_path / "arbin_test_file.res.gz"
    assert arbin_file_path.is_file()

    with open(arbin_file_path, "rb") as f_in:
        with gzip.open(temp_gz_file_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    assert temp_gz_file_path.is_file()

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
