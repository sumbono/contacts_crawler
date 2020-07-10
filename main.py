from parser_raw_contacts import raw_contacts, get_indiv
from google_linkedin_enricher import login, enricher

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
import time
import tldextract
from tqdm import tqdm
import json

def get_raw_data(url):
    return raw_contacts(get_indiv(url))

def enrich_data(raw_data,uname,pswd):
    all_data = []

    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1366x768')
    driver = webdriver.Chrome(options=options)
    logged_driver = login(driver,uname,pswd)
    
    for contact_data in tqdm(raw_data,ncols=85,desc=f"Processing enrichment for {len(raw_data)} contacts"):
        crawled_data = enricher(logged_driver,contact_data)
        all_data.append(crawled_data)

    driver.quit()

    with open(f"enriched_contacts.json", "w+", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    url = "https://www.startupsg.net/api/v0/search/profiles/individual?type=listing&sort=-changed&from=0&size=4780"
    raw_data = get_raw_data(url)
    
    uname = 'youremail@example.com'
    pswd = 'YourPassword'
    enrich_data(raw_data[:100],uname,pswd)
