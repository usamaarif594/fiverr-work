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

# Mapping van eigenaar en beurs
OWNER_MAPPING = {
    '1': {'id': '1388563141', 'name': 'Cas den Braber', 'email': 'cas@kartent.nl', 'firstname': 'Cas'},
    '2': {'id': '1110915562', 'name': 'Timo Krenn', 'email': 'timo@kartent.com', 'firstname': 'Timo'},
    '3': {'id': '1793614525', 'name': 'Sam Steins Bisschop', 'email': 'sam@kartent.nl', 'firstname': 'Sam'},
    '4': {'id': '1158007761', 'name': 'Jan Portheine', 'email': 'jan@kartent.com', 'firstname': 'Jan'}
}

FAIR_MAPPING = {
    '1': "METAVAK Gorinchem - 2024",
    '2': "Interieur Collectie Dagen - 2024",
    '3': "Installatie Vakbeurs - 2024",
    '4': "Camperbeurs Hardenberg - 2024",
    '5': "Trendz Najaar - 2024",
    '6': "Welding Week Nederland - 2024",
    '7': "Heroes Dutch Comic Con Utrecht - 2024",
    '8': "Huis & Woon Beurs Hardenberg - 2024",
    '9': "Dutch Pork Expo Den Bosch - 2024",
    '10': "Dutch Poultry Expo Den Bosch - 2024",
    '11': "Rundvee & Mechanisatie Vakdagen (RMV) Hardenberg - 2024",
    '12': "Familiedagen Gorinchem - 2024",
    '13': "Winterfair Hardenberg - 2024",
    '14': "Vakbeurs Recycling - 2024",
    '15': "Recreatie Vakbeurs - 2024",
    '16': "Future Lighting - 2024",
    '17': "Rundvee & Mechanisatie Vakdagen (RMV) Gorinchem - 2024",
    '18': "De Groene Sector Vakbeurs Hardenberg - 2025",
    '19': "Trendz Voorjaar - 2025",
    '20': "Horeca Vakbeurs - 2025",
    '21': "Auto Prof Gorinchem - 2025",
    '22': "Infra Relatiedagen Hardenberg - 2025",
    '23': "Recreatie Next Level - 2025",
    '24': "HortiContact - 2025",
    '25': "Bakkersvak & IJs-vak - 2025",
    '26': "StocExpo - 2025",
    '27': "Aqua Nederland - 2025",
    '28': "Visualize Expo - 2025",
    '29': "Empack Den Bosch - 2025",
    '30': "Maakindustrie Expo - 2025",
    '31': "Worksafe Gorinchem - 2025",
    '32': "Maritime Industry Gorinchem - 2025",
    '33': "M+R Rotterdam - 2025",
    '34': "Pumps & Valves Rotterdam - 2025",
    '35': "Solids Rotterdam - 2025"
}

def get_normal_driver():
    chromedriver_path = "chromedriver.exe"
    service = Service(chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    return webdriver.Chrome(service=service, options=options)

def get_element_text(driver, locator):
    return WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

def input_element(driver, locator, text):
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    element.clear()
    element.send_keys(text)

def click_using_js(driver, locator):
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator))
    driver.execute_script("arguments[0].click();", element)

def clean_company_name(name):
    return re.sub(r'\s+B\.?V\.?$', '', name.strip())

def generate_fake_url(company_name):
    clean_name = re.sub(r'\s+', '', company_name)
    return f'www.{clean_name.lower()}.nl'

def get_personalized_message(company_name, event_name, is_first_outreach, owner_firstname, owner_email):
    clean_name = clean_company_name(company_name)
    if is_first_outreach:
        return f'''Hoi!
Leuk dat jullie met {clean_name} meedoen aan de {event_name}!
Ik wil jullie graag iets tofs laten zien: we maken bij KarTent unieke beursstands van gerecycled karton. Helemaal naar wens bedrukt en super duurzaam. Echt een eyecatcher!
Of je nu een hele stand wilt of een coole toevoeging aan je huidige setup, we kunnen samen iets geweldigs maken.
Zin om volgende week even te bellen en te kijken hoe we jullie kunnen laten shinen op de beurs?
Je kunt me bereiken op {owner_email} of 020-2612910.
Groetjes,
{owner_firstname} | KarTent'''
    else:
        return f'''Beste {clean_name},
Ik hoop dat dit bericht jullie goed bereikt. Onlangs stuurde mijn collega een berichtje over onze duurzame kartonnen stands voor {event_name}. Ik vroeg me af of jullie dit hebben ontvangen?
We zouden graag met jullie meedenken over hoe we jullie presentatie op de beurs nog specialer kunnen maken. Hebben jullie misschien interesse om hier volgende week kort over te bellen?
Ik kijk uit naar jullie reactie!
Groetjes,
{owner_firstname} | KarTent'''

def process_companies():
    url = input('Enter the URL: ')
    event_name = input('Enter the event name: ')
    is_first_outreach = input('Is this the first outreach? (yes/no): ').lower() == 'yes'
    
    print("Select the company owner:")
    for key, value in OWNER_MAPPING.items():
        print(f"{key}. {value['name']}")
    owner_choice = input("Enter the number of the company owner: ")
    owner_id = OWNER_MAPPING[owner_choice]['id']
    owner_name = OWNER_MAPPING[owner_choice]['name']
    owner_email = OWNER_MAPPING[owner_choice]['email']
    owner_firstname = OWNER_MAPPING[owner_choice]['firstname']

    print("Select the fair:")
    for key, value in FAIR_MAPPING.items():
        print(f"{key}. {value}")
    fair_choice = input("Enter the number of the fair: ")
    fair_name = FAIR_MAPPING[fair_choice]

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'outreach_{timestamp}.csv'
    
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Company Name', 'Company URL', 'Event Name', 'Owner Name', 'Fair Name', 'Reactie', 'Benaderd Op'])

    with open('negative_Companies.txt', 'r') as file:
        negative_companies = set(line.strip().lower() for line in file)

    driver = None

    try:
        driver = get_normal_driver()
        driver.get(url)
        main_window = driver.current_window_handle
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-name='result_counts']"))
        )

        company_name_xpath = "(//div/h3/a)"
        company_names = driver.find_elements(By.XPATH, company_name_xpath)

        for company_element in company_names:
            company_name = company_element.text.strip()
            print(f"Found company: {company_name}")

            if company_name.lower() in negative_companies:
                print(f"Skipping {company_name} as it is in the negative companies list.")
                continue

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
                
                print(f"Form submitted for {company_name}")
                
                with open(csv_filename, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([company_name, company_url, event_name, owner_name, fair_name, "No", datetime.now().strftime("%Y-%m-%d")])
            except Exception as e:
                print(f'Failed to process form for {company_name}: {str(e)}')
                with open(csv_filename, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([company_name, company_url, event_name, owner_name, fair_name, "Failed", datetime.now().strftime("%Y-%m-%d")])
            finally:
                driver.close()
                driver.switch_to.window(main_window)

    except Exception as e:
        print(f'An error occurred while processing the companies: {str(e)}\nPlease try again...')
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    process_companies()
