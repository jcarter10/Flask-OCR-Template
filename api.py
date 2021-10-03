import os
import json
from flask import Flask, render_template, request, redirect

# local imports
import ocr

# vars
app = Flask(__name__)

# handles file upload and calls OCR script
@app.route("/upload_file", methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # get file and file name from request
        file = request.files['file']
        file_name = file.filename

        # validate file
        if file_name == '':
            return render_template('index.html', error_message="User did not upload a file. Try again...")
        if os.path.splitext(file_name)[1] != '.pdf':
            return render_template('index.html', error_message="User uploaded a file with a '" + os.path.splitext(file_name)[1] + "' extension, please upload PDF (.pdf) files only. Try again...")

        # create file path
        file_path = 'pdfs/' + file_name

        # save file temporarily 
        csvFile = open(file_path, "wb")
        csvFile.write(file.read())
        csvFile.close()
        
        # call OCR
        result_list = ocr.startProcess(file_path)

        # file not needed anymore so remove
        os.remove(file_path)

        return render_template('index.html', file_name=file_name, result_list=result_list)

    # reroute to home page for GET requests
    if request.method == 'GET':
        return redirect('/', code=301)

# renders the UI
@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')

# starts flask
if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True, threaded=True)