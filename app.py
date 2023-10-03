import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/get', methods=['POST'])
def get_energy_bill():
    try:
        # Configure Chrome to run in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # Get consumer_no and office_address_value from the request JSON
        data = request.json
        consumer_no = data.get("consumer_no")
        office_address_value = data.get("office_address_value")

        # Create a Selenium webdriver with headless mode
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.jseb.co.in/WSS/WSSUI/frmpwlEnergyBillPayment.aspx")

        # Wait for the page to load and the JavaScript to execute
        driver.implicitly_wait(10)

        # Select the "Consumer No." radio button
        consumer_radio_button = driver.find_element(By.ID, "ctl00_cphpwl_rbtAccountNumber")
        consumer_radio_button.click()

        # Enter the Consumer No. in the input box
        consumer_input = driver.find_element(By.ID, "ctl00_cphpwl_txtConsumerNumber")
        consumer_input.send_keys(consumer_no)

        # Select the Office Address from the dropdown menu
        office_address_dropdown = driver.find_element(By.ID, "ctl00_cphpwl_ddlOfficeAddress")
        for option in office_address_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.get_attribute("value") == office_address_value:
                option.click()
                break

        # Click the "Get Bill Details" button using JavaScript
        driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "ctl00_cphpwl_btnGetBillDetail"))

        # Wait for the page to redirect and load
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "ctl00_cphpwl_lblConsumerName")))

        # Extract data from the redirected page
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Find the required data and store it in a dictionary
        data = {
            "Consumer Name": soup.find("span", {"id": "ctl00_cphpwl_lblConsumerName"}).text.strip(),
            "Bill No.": soup.find("span", {"id": "ctl00_cphpwl_lblBillNo"}).text.strip(),
            "KNo": soup.find("span", {"id": "ctl00_cphpwl_lblKNo1"}).text.strip(),
            "Bill Month": soup.find("span", {"id": "ctl00_cphpwl_lblBillMonth"}).text.strip(),
            "Due Date": soup.find("span", {"id": "ctl00_cphpwl_lblDueDate"}).text.strip(),
            "Bill Amount (Rs.)": soup.find("span", {"id": "ctl00_cphpwl_lblBilledAmount"}).text.strip(),
            "Amount Payable (Rs.)": soup.find("span", {"id": "ctl00_cphpwl_lblAmountPayble"}).text.strip(),
        }

        # Close the browser
        driver.quit()

        # Return the JSON response
        return jsonify({"result": data})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
