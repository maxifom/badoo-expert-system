import datetime
import logging
from time import sleep

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

if __name__ == '__main__':
    # driver = webdriver.RemoteWebDriver(desired_capabilities=DesiredCapabilities.CHROME)
    while True:
        try:
            driver = webdriver.Chrome(chrome_options=webdriver.ChromeOptions(), executable_path="./chromedriver")
            driver.get("https://badoo.com")
            driver.add_cookie({
                "name": "s1",
                "value": "s1%3A532%3AGSAe6BDjuGMil7d107cOwCom7iGn1qeeKjFjGVL2",
                "domain": ".badoo.com",
            })
            driver.get("https://badoo.com/encounters")
            while True:
                sleep(1)
                element = WebDriverWait(driver=driver, timeout=600).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'js-profile-header-name'))
                )
                print("Parsing telka: ", driver.find_element_by_class_name("profile-header__user").text)
                element.click()
                WebDriverWait(driver=driver, timeout=600).until(
                    EC.presence_of_element_located((By.ID, 'photo_list'))
                )
                sleep(1)
                t = datetime.datetime.now().timestamp()
                html1 = driver.page_source
                with open("html/{}.html".format(t), "w") as f:
                    f.write(html1)
                driver.find_element_by_tag_name("html").send_keys("2")
        except:
            logging.exception("")
            pass
        finally:
            driver.quit()
