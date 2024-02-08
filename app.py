import requests
from flask import Flask, request
# Import the required modules
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
import os
import whisper
import warnings
warnings.filterwarnings("ignore")
from selenium.webdriver.firefox.options import Options
model = whisper.load_model("base")

def transcribe(url):
    with open('.temp', 'wb') as f:
        f.write(requests.get(url).content)
    result = model.transcribe('.temp')
    return result["text"].strip()

def click_checkbox(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='reCAPTCHA']"))
    driver.find_element(By.ID, "recaptcha-anchor-label").click()
    driver.switch_to.default_content()

def request_audio_version(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='recaptcha challenge expires in two minutes']"))
    driver.find_element(By.ID, "recaptcha-audio-button").click()

def solve_audio_captcha(driver):
    text = transcribe(driver.find_element(By.ID, "audio-source").get_attribute('src'))
    driver.find_element(By.ID, "audio-response").send_keys(text)
    driver.find_element(By.ID, "recaptcha-verify-button").click()
    time.sleep(5)
    driver.refresh()
    link = driver.find_element(By.CLASS_NAME, "link").get_attribute('href')
    return link


app = Flask(__name__)

@app.route('/get_response')
def get_response():
    url = request.args.get('url')

    if not url:
        return "Please provide a URL as a query parameter (e.g., /get_response?url=https://example.com)", 400

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get(request.args.get('url'))
        click_checkbox(driver)
        time.sleep(1)
        request_audio_version(driver)
        time.sleep(1)
        link = solve_audio_captcha(driver)
        time.sleep(10)
        
        return f'{link}', response.status_code
    except requests.exceptions.RequestException as e:
        return str(e), 500

# if __name__ == '__main__':
#     app.run(debug=True)
