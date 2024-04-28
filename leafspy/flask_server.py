"""API and server for Leafs"""

import os
from pathlib import Path
import random
import logging
import string
import gzip

from flask import Flask, request, send_from_directory
from werkzeug.utils import secure_filename

from .data_handler import functions
from .supported_experiments import (
    accepted_files,
    accepted_combinations,
    accepted_instruments,
    accepted_tests,
)


UPLOAD_FOLDER = "./uploads"
ALLOWED_OPTIONAL_KEYWORD_ARGUMENTS = [
    "data_format_model",
]

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def temporary_storage_path(extension):
    """Path to a temporary directory for storing intermediate file(s)."""

    new_file_name = (
        "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(25)
        )
        + "."
        + extension.lower()
    )
    upload_folder = Path(app.config["UPLOAD_FOLDER"]).resolve()
    if not upload_folder.is_dir():
        logging.debug("upload folder does not exist")
        logging.debug("creating upload folder")
        os.mkdir(upload_folder)
    return upload_folder / new_file_name


def check_gzip(filename):
    """Check that the file is a gzip file."""

    return Path(filename).suffix == ".gz"


def allowed_test(extension, test_type, instrument):
    """Check if the file is appropriate type."""

    logging.debug(f"File info: {extension=}, {test_type=}, {instrument=}")
    logging.debug(f"Accepted tests: {accepted_tests}")

    if extension not in accepted_files:
        return (
            False,
            f"{extension} extension not yet supported, currently we support the following files {accepted_files}",
            "",
        )
    if test_type not in accepted_tests:
        return (
            False,
            f"{test_type} test not yet supported, currently we support the following tests {accepted_tests}",
            "",
        )
    if instrument not in accepted_instruments:
        return (
            False,
            f"{instrument} not yet supported, currently we support the following instruments {accepted_instruments}",
            "",
        )

    file_index = accepted_files.index(extension)
    test_index = accepted_tests.index(test_type)
    instrument_index = accepted_instruments.index(instrument)

    logging.debug(f"Combination: {file_index=}, {test_index=}, {instrument_index=}")
    if test_index in accepted_combinations[file_index].keys():
        if instrument_index in accepted_combinations[file_index][test_index]:
            return (
                True,
                "",
                accepted_combinations[file_index][test_index][instrument_index],
            )
        else:
            logging.debug("Rejected - not acceptable combination! ")
            return (
                False,
                f"{instrument} {test_type} tests are not supported in {extension} files",
                "",
            )
    else:
        logging.debug(
            "Rejected - file index not valid key in accepted combinations dict! "
        )
        return False, f"{test_type} test is not supported in {extension} files.", ""


@app.errorhandler(404)
def page_not_found(error):
    """404."""

    logging.debug(f"404: {error}")
    return "This page does not exist", 404


@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    """Route for posting files."""
    logging.debug(f"Request method: {request.method}")

    if request.method != "POST":
        out = """
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        """
        return out

    test_type = request.form.get("test_type")
    test_type_subcategory = request.form.get("test_type_subcategory")
    instrument = request.form.get("instrument")
    brand = request.form.get("instrument_brand")

    optional_key_word_arguments = {}
    for optional_kwarg in ALLOWED_OPTIONAL_KEYWORD_ARGUMENTS:
        if optional_kw_value := request.form.get(optional_kwarg):
            optional_key_word_arguments[
                optional_kwarg
            ] = optional_kw_value  # this might be case-sensitive

    if not brand:
        return {"Code": 1, "Message": "Please provide an instrument brand"}

    if not instrument:
        return {"Code": 1, "Message": "Please provide an instrument"}

    if not test_type:
        return {"Code": 1, "Message": "Please provide a test type"}

    if test_type == "XRD":
        test_type = test_type
    else:
        test_type = "-".join([test_type, test_type_subcategory])

    instrument = brand + "-" + instrument

    files = request.files.getlist("files")

    if len(files) == 0:
        return {"Code": 1, "Message": "No file attached"}

    # only supporting one file at the moment:
    file = files[0]

    if not check_gzip(file.filename):
        return {"Code": 1, "Message": "Only gz files allowed"}

    extension = file.filename.rsplit(".", maxsplit=2)[-2].upper()
    filename = secure_filename(file.filename.rsplit(".", maxsplit=2)[0])
    if filename == "":
        return {"Code": 1, "Message": "File has no name"}

    file = gzip.open(file, "rb")
    file = file.read()
    if not file:
        return {"Code": 1, "Message": "File is empty"}

    allowed, message, data_converter = allowed_test(
        extension, test_type.upper(), instrument.upper()
    )
    if not allowed:
        return {"Code": 1, "Message": message}

    location = temporary_storage_path(extension)
    with open(location, "wb") as f_out:
        f_out.write(file)

    success, data = functions[data_converter](
        location,
        instrument=instrument.upper(),
        test_type=test_type.upper(),
        extension=extension.upper(),
        **optional_key_word_arguments,
    )

    if success:
        if len(files) > 1:
            # message={'Code':0, 'Message':f"Transformed successfully. Only the first file ({filename}) was transformed, multiple file transformation is not yet supported."}
            # return {'experiment_info': data['experiment_info'], 'experiment_summary': data['experiment_summary'], 'experiment_data': data['experiment_data']}
            return data
        # return {'experiment_info': data['experiment_info'], 'experiment_summary': data['experiment_summary'],'experiment_data': data['experiment_data']}
        return data

    else:
        return {
            "Code": 1,
            "Message": "Unknown Error while transforming file.",
        }


@app.route("/uploads/<name>")
def download_file(name):
    """Route to get file from uploads folder."""

    # This seems not to be in use?
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
