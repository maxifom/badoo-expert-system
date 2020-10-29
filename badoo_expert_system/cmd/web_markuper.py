import sqlite3

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import json_response


@aiohttp_jinja2.template("index.jinja2")
async def hello(request):
    return {}


async def get_image(request):
    c = request.app["db"].cursor()
    c.execute("""SELECT *
FROM face_embeddings
WHERE status IS NULL
  AND length(face_embeddings) > 2
ORDER BY RANDOM()
LIMIT 1
""")
    q = c.fetchone()
    c.execute("""SELECT status, COUNT(1)
FROM face_embeddings
WHERE length(face_embeddings) > 2
GROUP BY status
    """)
    w = c.fetchall()
    c.close()
    total = w[0][1] + w[1][1] + w[2][1] + w[3][1]
    return json_response({
        "id": q[0],
        "filename": q[1],
        "total": total,
        "solved": w[1][1] + w[2][1] + w[3][1],
    })


async def update_status(request: Request):
    db = request.app["db"]
    j = await request.json()
    db.execute("UPDATE face_embeddings SET status = ? WHERE id = ?", (j["status"], j["id"]))
    db.commit()

    return json_response({"status": "updated"})


def main():
    app = web.Application()
    db = sqlite3.connect("face_embeddings.sqlite")
    app.update(db=db)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))
    app.add_routes([
        web.get("/", hello),
        web.get("/get_image", get_image),
        web.post("/update_status", update_status),
        web.static("/static", "imgs_with_faces")
    ])

    web.run_app(app, port=8080)


# Разметка
if __name__ == '__main__':
    main()
