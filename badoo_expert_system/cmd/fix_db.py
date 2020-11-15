import json
import sqlite3

if __name__ == '__main__':
    db = sqlite3.connect("face_embeddings.sqlite")
    c = db.cursor()
    c.execute("SELECT * FROM face_embeddings WHERE status IS NOT NULL")
    rows = c.fetchall()
    for i in rows:
        embedding = i[2]
        length = len(json.loads(embedding))
        if length >= 2:
            c.execute("UPDATE face_embeddings SET status = NULL WHERE id = ?", (i[0],))
        print(length)
    db.commit()
