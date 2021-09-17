import os
from re import split
from flask import Flask, flash, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from data_handler import functions
from SupportedTests import accepted_files, accepted_combinations, accepted_instruments, accepted_tests
import random
import string
import gzip


UPLOAD_FOLDER = './uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def check_gzip(filename):
    splitted = filename.split(".")
    return len(splitted) > 2 and splitted[2] =="gz"

def allowed_test(extension, test_type, instrument):
    if extension not in accepted_files: 
        return (False, f"{extension} extension not yet supported, currently we support the following files {accepted_files}","")
    if test_type not in accepted_tests:
        return (False, f"{test_type} test not yet supported, currently we support the following tests {accepted_tests}","") 
    if instrument not in accepted_instruments:
        return (False, f"{instrument} not yet supported, currently we support the following instruments {accepted_instruments}","")
    file_index = accepted_files.index(extension)
    test_index = accepted_tests.index(test_type)
    instrument_index = accepted_instruments.index(instrument)
    if test_index in accepted_combinations[file_index].keys():
        if instrument_index in accepted_combinations[file_index][test_index]:
            return (True, "", accepted_combinations[file_index][test_index][instrument_index])
        else:
            return (False, f"{instrument} {test_type} tests are not supported in {extension} files","")
    else:
        return (False, f"{test_type} test is not supported in {extension} files.","")

@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        test_type = request.form.get("test_type")
        test_type_subcategory = request.form.get("test_type_subcategory")
        instrument = request.form.get("instrument")
        brand = request.form.get("instrument_brand")
        if not brand:
            return {'Code':1, 'Message':'Please provide an instrument brand'}
        if not instrument:
            return {'Code':1, 'Message':'Please provide an instrument'}
        if not test_type:
            return {'Code':1, 'Message':'Please provide a test type'}
        if test_type == "XRD":
            test_type = test_type
        else:
            test_type = test_type= test_type + "-" + test_type_subcategory
            
            #if not test_subtype:
            #return {'Code':1, 'Message':'Please provide a subtest type'}
            
        #    return {'Code':1, 'Message':'Please provide a test subtype'}
        instrument = brand + "-" + instrument
        #if not test_subtype:
        #    test_type = test_type
        #else: 
        #    test_type= test_type + "-" + test_subtype
        files = request.files.getlist('files')
        if len(files) == 0:
            return {'Code':1, 'Message': "No file attached"}

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        file = files[0]
        if not check_gzip(file.filename):
            return {'Code':1 , 'Message': "Only gz files allowed"}
        extension= file.filename.rsplit('.')[1].upper()
        filename = secure_filename(file.filename.rsplit('.')[0])
        file = gzip.open(file, 'rb')
        file = file.read() 
        if filename == '':
            return {'Code':1, 'Message': "File has no name"}
        if file:
            allowed, message, data_converter = allowed_test(extension, test_type.upper(), instrument.upper())
            if allowed:
                new_file_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25)) + "." + extension.lower()
                location  = os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], new_file_name))
                print(location)
                with open(location , 'wb') as f_out:
                    f_out.write(file)   
                success, data = functions[data_converter]('uploads/' + new_file_name)
                #print(f'{extension}: {test_type.upper()} :{instrument.upper}')
                if success:
                    if len(files) > 1:
                        #message={'Code':0, 'Message':f"Transformed successfully. Only the first file ({filename}) was transformed, multiple file transformation is not yet supported."}
                        #return {'experiment_info': data['experiment_info'], 'experiment_summary': data['experiment_summary'], 'experiment_data': data['experiment_data']} 
                        return data
                    #return {'experiment_info': data['experiment_info'], 'experiment_summary': data['experiment_summary'],'experiment_data': data['experiment_data']}
                    return data

                else:
                    return{'Code':1, 'Message': "Unknown Error while transforming file."}
            else:
                return {'Code':1, 'Message': message }

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)