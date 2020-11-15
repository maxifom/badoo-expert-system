import os
import random
import string

import math
import numpy as np
import face_recognition
import aiohttp_jinja2
import jinja2
import joblib
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sklearn.calibration import CalibratedClassifierCV


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
    arr = np.array(face_embeddings_json[0], dtype=np.float32).reshape(1, -1)
    prediction = clf.predict(arr).tolist()[0]
    percentages = clf.predict_proba(arr).tolist()
    perc = {}
    for c, p in zip(clf.classes_.tolist(), percentages[0]):
        perc[str(c)] = str(round(float(p) * 100, 2)) + "%"

    return {"image": fname, "prediction": prediction, "percentages": perc}


@aiohttp_jinja2.template("index_verification.jinja2")
async def hello(request):
    return {}


def main():
    app = web.Application()
    clf = joblib.load("clf.joblib")
    app.update(clf=clf)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))
    app.add_routes([
        web.get("/", hello),
        web.post("/upload", upload),
        web.static("/static", "verification_imgs")
    ])

    web.run_app(app, port=8080)


if __name__ == '__main__':
    main()
