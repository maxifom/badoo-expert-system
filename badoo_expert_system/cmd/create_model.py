import json
import sqlite3

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def create_model():
    db = sqlite3.connect("face_embeddings.sqlite")
    db.row_factory = dict_factory
    c = db.cursor()
    c.execute("SELECT * FROM face_embeddings")
    new_rows = []
    for r in c.fetchall():
        fe = json.loads(r["face_embeddings"])
        status = r["status"]
        if status is None:
            continue
        if r["status"] == 0:
            r.update(status=-1)
        r.update(face_embeddings=fe[0] if len(fe) > 0 else [], status=status)
        new_rows.append(r)
    status_1_rows = [n for n in new_rows if n['status'] == 1]
    status_m1_rows = [n for n in new_rows if n['status'] == -1][-len(status_1_rows):]
    dataset = status_1_rows + status_m1_rows
    y = [r["status"] for r in dataset]
    x = [r["face_embeddings"] for r in dataset]
    x_train, x_test, y_train, y_test = map(np.array, train_test_split(x, y, test_size=0.25, random_state=1))

    svc = LinearSVC()
    clf = CalibratedClassifierCV(svc)
    clf.fit(x_train, y_train)
    acc_svc = accuracy_score(y_test, clf.predict(x_test))
    print(classification_report(y_test, clf.predict(x_test)))
    print(f"Accuracy: {acc_svc}")
    print(f"Classes: {clf.classes_}")
    db.close()
    return clf


def main():
    filename = "clf.joblib"
    clf = create_model()
    joblib.dump(clf, filename)
    print(f"Dumped to file {filename}")



if __name__ == '__main__':
    main()
