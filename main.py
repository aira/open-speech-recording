import random

from flask import Flask
from flask import abort
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from werkzeug.utils import secure_filename

# from google.cloud import storage

import os
import uuid

app = Flask(__name__)

# Configure environment variables via app.yaml for deployment to Google Cloud Services
FLASK_PORT = 80  # for debug it's 5000
# Flask keys are typically 24-31 characters long and can be any ascii character, but most examples are just a-f and 0-9
# Django keys are only printable ASCII characters and all seem to be 50 characters long
SESSION_SECRET_KEY_LEN = 30  # DJANGO = 50
SESSION_SECRET_KEY_CHARS = 'abcdef0123456789'  # DJANGO = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

os.environ['CLOUD_STORAGE_BUCKET'] = CLOUD_STORAGE_BUCKET = (
    os.environ.get('CLOUD_STORAGE_BUCKET') or 'aira-ai-training-data')
os.environ['SESSION_SECRET_KEY'] = SESSION_SECRET_KEY = (
    os.environ.get('SESSION_SECRET_KEY') or
    ''.join([random.SystemRandom().choice(SESSION_SECRET_KEY_CHARS) for i in range(SESSION_SECRET_KEY_LEN)]))
# [end config]
storage = None


@app.route("/")
def welcome():
    session_id = request.cookies.get('session_id')
    if session_id:
        all_done = request.cookies.get('all_done')
        if all_done:
            return render_template("thanks.html")
        else:
            return render_template("record.html")
    else:
        return render_template("welcome.html")


@app.route("/legal")
def legal():
    return render_template("legal.html")


@app.route("/start")
def start():
    response = make_response(redirect('/'))
    session_id = uuid.uuid4().hex
    response.set_cookie('session_id', session_id)
    return response


@app.route('/upload', methods=['POST'])
def upload():
    session_id = request.cookies.get('session_id')
    if not session_id:
        make_response('No session', 400)
    word = request.args.get('word')
    audio_data = request.data
    filename = word + '_' + session_id + '_' + uuid.uuid4().hex + '.ogg'
    secure_name = secure_filename(filename)
    # Left in for debugging purposes. If you comment this back in, the data
    # will be saved to the local file system.
    with open(os.path.join('data', secure_name), 'wb') as f:
        f.write(audio_data)

    if storage:
        # Create a Cloud Storage client.
        gcs = storage.Client()
        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
        blob = bucket.blob(secure_name)
        blob.upload_from_string(audio_data, content_type='audio/ogg')
    return make_response("All good")


# CSRF protection, see http://flask.pocoo.org/snippets/3/.
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session['_csrf_token']
        if not token or token != request.args.get('_csrf_token'):
            abort(403)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = uuid.uuid4().hex
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token
# Change this to your own number before you deploy.
app.secret_key = SESSION_SECRET_KEY

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
