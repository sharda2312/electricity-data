import json
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

@app.route('/scrape_attendance', methods=['POST'])
def scrape_attendance():
    # Get JSON input from the POST request
    data = request.get_json()

    # Extract username and password from the JSON input
    username = data.get('username')
    password = data.get('password')

    # Configure Chrome to run in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")  # For Linux systems

    # Create a Selenium webdriver with headless mode
    driver = webdriver.Chrome(options=chrome_options)
    
    # Log in to the website
    login_url = "https://ums.paruluniversity.ac.in/Login.aspx"
    driver.get(login_url)

    username_input = driver.find_element(By.ID, "txtUsername")
    password_input = driver.find_element(By.ID, "txtPassword")
    login_button = driver.find_element(By.ID, "btnLogin")

    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

    # Wait for the page to load
    driver.implicitly_wait(10)  # Use implicit wait instead of time.sleep to wait for elements

    # Visit the attendance page
    attendance_url = "https://ums.paruluniversity.ac.in/StudentPanel/TTM_Attendance/TTM_Attendance_StudentAttendance.aspx"
    driver.get(attendance_url)

    # Wait for the attendance data to load (you may need to adjust the wait time)
    driver.implicitly_wait(10)

    # Parse the attendance data
    attendance_element = driver.find_element(By.ID, "ctl00_cphPageContent_lblPresentPCTCount")
    attendance = attendance_element.text

    # Create a JSON response
    attendance_data = {
        "Attendance": attendance
    }

    # Close the browser
    driver.quit()

    return jsonify(attendance_data)

if __name__ == '__main__':
    app.run(debug=True)
