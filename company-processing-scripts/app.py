import streamlit as st
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re
from datetime import datetime
import os

# Mapping of owner details
OWNER_MAPPING = {
    1: {'id': '1388563141', 'name': 'Cas den Braber', 'email': 'cas@kartent.nl', 'firstname': 'Cas'},
    2: {'id': '1110915562', 'name': 'Timo Krenn', 'email': 'timo@kartent.com', 'firstname': 'Timo'},
    3: {'id': '1793614525', 'name': 'Sam Steins Bisschop', 'email': 'sam@kartent.nl', 'firstname': 'Sam'},
    4: {'id': '1158007761', 'name': 'Jan Portheine', 'email': 'jan@kartent.com', 'firstname': 'Jan'}
}

# Mapping of fair details
FAIR_MAPPING = {
    1: 'METAVAK Gorinchem - 2024',
    2: 'Interieur Collectie Dagen - 2024',
    3: 'Installatie Vakbeurs - 2024',
    4: 'Camperbeurs Hardenberg - 2024',
    5: 'Trendz Najaar - 2024',
    6: 'Welding Week Nederland - 2024',
    7: 'Heroes Dutch Comic Con Utrecht - 2024',
    8: 'Huis & Woon Beurs Hardenberg - 2024',
    9: 'Dutch Pork Expo Den Bosch - 2024',
    10: 'Dutch Poultry Expo Den Bosch - 2024',
    11: 'Rundvee & Mechanisatie Vakdagen (RMV) Hardenberg - 2024',
    12: 'Familiedagen Gorinchem - 2024',
    13: 'Winterfair Hardenberg - 2024',
    14: 'Vakbeurs Recycling - 2024',
    15: 'Recreatie Vakbeurs - 2024',
    16: 'Future Lighting - 2024',
    17: 'Rundvee & Mechanisatie Vakdagen (RMV) Gorinchem - 2024',
    18: 'De Groene Sector Vakbeurs Hardenberg - 2025',
    19: 'Trendz Voorjaar - 2025',
    20: 'Horeca Vakbeurs - 2025',
    21: 'Auto Prof Gorinchem - 2025',
    22: 'Infra Relatiedagen Hardenberg - 2025',
    23: 'Recreatie Next Level - 2025',
    24: 'HortiContact - 2025',
    25: 'Bakkersvak & IJs-vak - 2025',
    26: 'StocExpo - 2025',
    27: 'Aqua Nederland - 2025',
    28: 'Visualize Expo - 2025',
    29: 'Empack Den Bosch - 2025',
    30: 'Maakindustrie Expo - 2025',
    31: 'Worksafe Gorinchem - 2025',
    32: 'Maritime Industry Gorinchem - 2025',
    33: 'M+R Rotterdam - 2025',
    34: 'Pumps & Valves Rotterdam - 2025',
    35: 'Solids Rotterdam - 2025'
}

def process_companies(url, event_name, is_first_outreach, owner_name, fair_name):
    owner_details = OWNER_MAPPING[owner_name]
    owner_firstname = owner_details['firstname']
    owner_email = owner_details['email']

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'outreach_{timestamp}.csv'

    # Writing headers to the CSV
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Company Name', 'Company URL', 'Event Name', 'Owner Name', 'Fair Name', 'Reactie', 'Benaderd Op'])

    # Selenium driver setup
    driver = None

    try:
        driver = get_normal_driver()
        driver.get(url)
        main_window = driver.current_window_handle

        company_name_xpath = "(//div/h3/a)"
        company_names = driver.find_elements(By.XPATH, company_name_xpath)

        for company_element in company_names:
            company_name = company_element.text.strip()
            company_url = company_element.get_attribute('href')
            driver.execute_script("window.open(arguments[0], '_blank');", company_url)
            driver.switch_to.window(driver.window_handles[-1])

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='form-field-name']")))
                input_element(driver, (By.XPATH, "//input[@id='form-field-name']"), f"{owner_firstname} | KarTent")
                input_element(driver, (By.XPATH, "//input[@id='form-field-email']"), owner_email)
                personalized_message = get_personalized_message(company_name, event_name, is_first_outreach, owner_firstname, owner_email)
                input_element(driver, (By.XPATH, "//textarea[@id='form-field-message']"), personalized_message)
                click_using_js(driver, (By.XPATH, "//button[@type='submit']"))

                # Write to CSV
                with open(csv_filename, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([company_name, company_url, event_name, owner_details['name'], FAIR_MAPPING[fair_name], "No", datetime.now().strftime("%Y-%m-%d")])
            except Exception as e:
                # If error, log the failure
                with open(csv_filename, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([company_name, company_url, event_name, owner_details['name'], FAIR_MAPPING[fair_name], "Failed", datetime.now().strftime("%Y-%m-%d")])
            finally:
                driver.close()
                driver.switch_to.window(main_window)
            time.sleep(2)
    finally:
        if driver:
            driver.quit()
    
    return csv_filename

def display_options(options_dict, prompt):
    option_str = "\n".join([f"{key}. {value}" for key, value in options_dict.items()])
    st.text_area(prompt, option_str)
    choice = st.number_input(f"Enter the number of the {prompt.lower()}", min_value=1, max_value=len(options_dict))
    return choice

# Streamlit Interface
st.title("Outreach Automation App")

url = st.text_input("Enter the URL of the companies:")
event_name = st.text_input("Enter the Event Name:")
is_first_outreach = st.radio("Is this the first outreach?", ('Yes', 'No')) == 'Yes'

# Display options for owner and fair selection
owner_name = display_options(OWNER_MAPPING, "Select the company owner:")
fair_name = display_options(FAIR_MAPPING, "Select the fair:")

if st.button("Start Outreach"):
    csv_filename = process_companies(url, event_name, is_first_outreach, owner_name, fair_name)
    with open(csv_filename, 'rb') as f:
        st.download_button(
            label="Download CSV",
            data=f,
            file_name=csv_filename,
            mime='text/csv'
        )
    st.success("Outreach process completed!")
