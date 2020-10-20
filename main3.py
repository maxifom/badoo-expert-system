import json
import time
from os import listdir

import cv2
import face_recognition
import sqlite3

if __name__ == '__main__':
    db = sqlite3.connect("face_embeddings.sqlite")
    db.execute("""create table if not exists face_embeddings
(
	id INTEGER
		constraint face_embeddings_pk
			primary key autoincrement,
	original_filename TEXT,
	face_embeddings BLOB
);

""")
    cursor = db.cursor()
    dir = listdir("imgs")
    start_time = time.perf_counter()
    skipped = 0
    for i, d in enumerate(dir):
        cursor.execute("SELECT 1 FROM face_embeddings WHERE original_filename = ?", (d,))
        if cursor.fetchone():
            skipped += 1
            continue
        if skipped > 0:
            print(f"SKIPPED {skipped}")
        t = time.perf_counter()
        print(f"Parsing {d}. {i} / {len(dir)} {float(i / len(dir)) * 100:2f}%")
        image = face_recognition.load_image_file(f"imgs/{d}")
        face_locations = face_recognition.face_locations(image)
        face_embeddings = face_recognition.face_encodings(image)
        face_embeddings_json = json.dumps([f.tolist() for f in face_embeddings])
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(image, (left, top), (right, bottom),
                          (0, 255, 0), 2)
        cv2.imwrite(f"imgs_with_faces/{d}", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        db.execute("""INSERT INTO face_embeddings(original_filename, face_embeddings) VALUES(?,?)""",
                   (d, face_embeddings_json))
        db.commit()
        took = time.perf_counter() - t
        speed = float(i - skipped) / (time.perf_counter() - start_time)
        print(f"took {took:.2f}s, speed: {speed} per second")
