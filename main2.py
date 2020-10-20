import os
import shutil
from os.path import exists

from scrapy import Selector
import requests
from yarl import URL

if __name__ == '__main__':
    dir = os.listdir("html")
    for index_file, file in enumerate(dir):
        print(index_file, len(dir))
        full_file = "html/" + file
        with open(full_file) as f:
            html = f.read()
            s = Selector(text=html)
            images = []
            big_image_url = s.css("img.js-mm-photo::attr(src)").get()
            if big_image_url:
                ui = URL(big_image_url)
                d = dict(ui.query)
                d.update(size="9999x9999", wm_size='0x0', wm_offset='0x0')
                big_image_url = ui.with_query(d).with_scheme("https").__str__()
                images.append(big_image_url)
            images_1 = s.css("img.photo-list__img::attr(src)").getall()
            for i in images_1:
                ui = URL(i)
                d = dict(ui.query)
                d.update(size="9999x9999", wm_size='0x0', wm_offset='0x0')
                i = ui.with_query(d).with_scheme(
                    "https").__str__()
                images.append(i)
            for index, i in enumerate(images):
                filepath = "imgs/{}_{}.jpg".format(file, index)
                if exists(filepath):
                    print("SKIP ", filepath)
                    continue
                r = requests.get(i, stream=True)
                print(r.status_code)
                with open(filepath, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
                del r
