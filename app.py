import os
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime
import config
from utils import utils

load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/upload', methods=['POST'])
def upload_resumes():
    resumes = request.files.getlist('resumes')
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    for idx, file_data in enumerate(resumes):
        if file_data and utils.allowed_file(file_data.filename):
            filename = f"resume_{timestamp}_{idx+1}.{utils.get_extension(file_data.filename)}"
            file_path = os.path.join(config.RESUMES_PATH, filename)
            file_data.save(file_path)
    return "Success"

if (__name__ == '__main__'):
    app.run(host=os.environ.get("HOSTIP")  , port=os.environ.get("FLASK_RUN_PORT") , debug=True)