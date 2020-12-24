import json
import os
import random
import sqlite3
import string

import aiohttp_jinja2
import cv2
import face_recognition
import jinja2
import joblib
import numpy as np
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sklearn.calibration import CalibratedClassifierCV

from create_model import create_model, dict_factory


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


@aiohttp_jinja2.template("result.jinja2")
async def upload(request: Request):
    clf: CalibratedClassifierCV = request.app["clf"]
    data = await request.post()
    input_file = data['file'].file
    filename = data['file'].filename
    extension = filename.split(".")[-1]
    content = input_file.read()
    fname = get_random_string(16) + "." + extension
    filepath = os.path.join("verification_imgs", fname)
    with open(filepath, "wb") as f:
        f.write(content)

    image = face_recognition.load_image_file(filepath)
    face_embeddings = face_recognition.face_encodings(image)
    face_embeddings_json = [f.tolist() for f in face_embeddings]
    if len(face_embeddings_json) == 0:
        return json_response({"message": "No face found"})
    face_locations = face_recognition.face_locations(image)
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(image, (left, top), (right, bottom),
                      (0, 255, 0), 2)
    cv2.imwrite(filepath, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    arr = np.array(face_embeddings_json[0], dtype=np.float32).reshape(1, -1)
    prediction = clf.predict(arr).tolist()[0]
    percentages = clf.predict_proba(arr).tolist()
    perc = {}
    for c, p in zip(clf.classes_.tolist(), percentages[0]):
        perc[str(c)] = str(round(float(p) * 100, 2)) + "%"
    db = request.app['db']
    c = db.cursor()
    face_embeddings_json = json.dumps(face_embeddings_json)
    c.execute("""INSERT INTO face_embeddings(original_filename, face_embeddings, status) VALUES(?,?,?)""",
              (fname, face_embeddings_json, prediction))
    db.commit()
    id = c.lastrowid
    print(id)
    c.close()
    return {"image": fname, "prediction": prediction, "percentages": perc, 'id': id}


@aiohttp_jinja2.template("index_verification.jinja2")
async def hello(request):
    return {}


@aiohttp_jinja2.template("index_verification.jinja2")
async def upload_to_db(request: Request):
    data = await request.post()
    print(data)
    if data['status'] == '-1':
        db = request.app['db']
        c = db.cursor()
        c.execute("UPDATE face_embeddings SET status = status*-1 WHERE id = ?", (data['image_id'],))
        db.commit()
        c.close()
    filename = "clf.joblib"
    clf = create_model()
    request.app.update(clf=clf)
    joblib.dump(clf, filename)
    print(f"Dumped to file {filename}")
    return {}


def main():
    app = web.Application()
    clf = joblib.load("clf.joblib")
    db = sqlite3.connect("face_embeddings.sqlite")
    db.row_factory = dict_factory
    app.update(clf=clf, db=db)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))
    app.add_routes([
        web.get("/", hello),
        web.post("/upload", upload),
        web.static("/static", "verification_imgs"),
        web.post("/create_model", create_model),
        web.post('/upload_to_db', upload_to_db)
    ])

    web.run_app(app, host="127.0.0.1", port=8080)


if __name__ == '__main__':
    main()
