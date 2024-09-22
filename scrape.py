# Import necessary libraries
import argparse
import csv
import random
import time
import pandas as pd
import undetected_chromedriver as uc
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# Set up command-line arguments for the script
parser = argparse.ArgumentParser(description='Process some files.')
parser.add_argument('filename', help='the name of the file to process')
args = parser.parse_args()
filename = args.filename  # The name of the file to process

# Define the URL of the website to scrape
url = 'https://bizfilings.vermont.gov/online/DatabrokerInquire/'

# Define the columns for the output CSV file
columns = [
    "name",
    "detail_link",
    "registration_id",
    "address",
    "business_status"
]

# Create a new DataFrame with the defined columns and write it to the CSV file
pdata = pd.DataFrame(columns=columns)
pdata.to_csv(filename, mode='w', index=False, encoding="utf-8", quotechar='"', quoting=csv.QUOTE_ALL)

driver = uc.Chrome()
driver.get(url)
time.sleep(3)  # Wait for 3 seconds for the page to load
driver.find_element(By.ID, "btnSearch").click()
time.sleep(3)

element_token = driver.find_elements(By.NAME, "__RequestVerificationToken")
token = element_token[0].get_attribute("value")

cookies = driver.get_cookies()

cookie = ''
for val in cookies:
    cookie += val['name'] + '=' + val['value'] + ';'

headers = {
    "X-Requested-With": "XMLHttpRequest",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    '__requestverificationtoken': token,
    'Cookie': cookie
}

data = {
    'undefined': '',
    'sortby': 'BusinessID',
    'stype': 'a',
    'pidx': 1,
}

BusinessSearchListURL = 'https://bizfilings.vermont.gov/online/DatabrokerInquire/BusinessSearchList'


def get_data():
    response = requests.post(BusinessSearchListURL,
                             headers=headers, data=data)

    soup = BeautifulSoup(response.text, 'html.parser')

    rows = soup.find('tbody').find_all('tr')

    for row in rows:
        cols = row.find_all('td')

        name_tag = cols[0].find('a')
        name = name_tag.text.strip()
        detail_link = name_tag['href']

        registration_id = cols[1].text.strip()
        address = cols[2].text.strip()
        business_status = cols[3].text.strip()

        dataframe = pd.DataFrame([[name, detail_link, registration_id, address, business_status]], columns=columns)
        dataframe.to_csv(filename, mode='a', index=False, header=False, encoding="utf-8", quotechar='"',
                         quoting=csv.QUOTE_ALL)


for i in range(1, 38):
    data['pidx'] = i
    get_data()
    print(f'Page {i} done')
    time.sleep(random.randint(7, 15))

driver.quit()
