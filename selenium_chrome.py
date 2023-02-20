import os
import pickle
import sys
import time
import urllib

import pydub as pydub
import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")


def kinguin_logining(login, password):
    # user-agent
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    # options.add_argument("--headless")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options
                              )

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    driver.maximize_window()

    try:
        try:
            driver.get("https://www.kinguin.net/")

            for cookie in pickle.load(open(f"cookies", "rb")):
                driver.add_cookie(cookie)
            driver.get("https://www.kinguin.net/app/dashboard/expressorders")
            driver.find_element(By.CSS_SELECTOR,
                                '#app > div.sc-ug95qh-0.iKsmeF.c-header > div.sc-ug95qh-2.dWLPom.container > div.sc-ug95qh-1.dQLmya > div.sc-16u9mbc-0.tgXqR > a')
            time.sleep(10)
        except:

            driver.get("https://www.kinguin.net/app/dashboard/expressorders")
            time.sleep(5)
            if not driver.current_url.startswith('https://www.kinguin.net/app/dashboard/expressorders'):
                try:
                    sign_in_button = driver.find_element(By.CLASS_NAME, 'unlogged')
                    sign_in_button.click()
                    time.sleep(5)
                except:
                    email_input = driver.find_element(By.ID, 'user')
                    email_input.clear()
                    email_input.send_keys(login)

                    password_input = driver.find_element(By.ID, "password")
                    password_input.clear()
                    password_input.send_keys(password)
                    try:
                        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((
                            By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")))
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                            By.XPATH, "//span[@id='recaptcha-anchor']"))).click()
                        driver.switch_to.default_content()
                        WebDriverWait(driver, 10).until(
                            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,
                                                                       "iframe[title='recaptcha challenge expires in two minutes']")))
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, "recaptcha-audio-button"))).click()

                        # get the mp3 audio file
                        time.sleep(5)
                        src = driver.find_element(By.CLASS_NAME, "rc-audiochallenge-tdownload-link").get_attribute(
                            "href")
                        print(f"[INFO] Audio src: {src}")

                        path_to_mp3 = os.path.normpath(os.path.join(os.getcwd(), "sample.mp3"))
                        path_to_wav = os.path.normpath(os.path.join(os.getcwd(), "sample.wav"))

                        # download the mp3 audio file from the source
                        urllib.request.urlretrieve(src, path_to_mp3)

                        # load downloaded mp3 audio file as .wav
                        try:
                            sound = pydub.AudioSegment.from_mp3(path_to_mp3)
                            sound.export(path_to_wav, format="wav")
                            sample_audio = sr.AudioFile(path_to_wav)
                        except Exception:
                            sys.exit(
                                "[ERR] Please run program as administrator or download ffmpeg manually, "
                                "https://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/")

                        # translate audio to text with google voice recognition
                        time.sleep(3)

                        r = sr.Recognizer()
                        with sample_audio as source:
                            audio = r.record(source)
                        key = r.recognize_google(audio)
                        print(f"[INFO] Recaptcha Passcode: {key}")

                        # key in results and submit
                        driver.find_element(By.ID, "audio-response").send_keys(key.lower())
                        driver.find_element(By.ID, "audio-response").send_keys(Keys.ENTER)
                        driver.switch_to.default_content()

                        driver.find_element(By.ID, "recaptcha-demo-submit").click()

                    except:
                        pass
                    finally:
                        time.sleep(5)
                        driver.switch_to.parent_frame()
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, '_submit'))).click()
                        pickle.dump(driver.get_cookies(), open("cookies", "wb"))
                        print('Куки сохранены')

            time.sleep(30)


    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    kinguin_logining(login, password)
