from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
import time
from pymongo import MongoClient
import tldextract
from tqdm import tqdm

def login(driver,uname,pswd):
    driver.get('https://www.linkedin.com/login')
    driver.implicitly_wait(7)
    email = driver.find_element(By.ID,"username")
    password = driver.find_element(By.ID,"password")
    login = driver.find_element_by_css_selector('button[type="submit"]')
    email.send_keys(uname)
    password.send_keys(pswd)
    login.click()
    time.sleep(7)
    return driver

def googling(driver,contact_data):
    url = None
    contact_name = contact_data['contact_name']
    position = contact_data['position']
    company_name = ''
    if contact_data['company_name'] != None:
        company_name = contact_data['company_name']
    driver.get('https://www.google.com')
    driver.implicitly_wait(5)
    search_query = driver.find_element_by_name('q')
    search_query.send_keys(f'site:linkedin.com/in/ AND {contact_name} AND {position} AND {company_name}')
    search_query.send_keys(Keys.RETURN)
    time.sleep(5)
    url_raw = driver.find_elements_by_class_name('r')
    print(f"Length of url in google search result: {len(url_raw)}")
    if len(url_raw)>0:
        link_url_raw = url_raw[0].find_element_by_css_selector('a')
        url = link_url_raw.get_attribute('href')
    if url:
        linkedin_suffix = url.split('/')[-1]
        url = f"https://www.linkedin.com/in/{linkedin_suffix}"
    return url

def crawling(driver,url,contact_data):
    contact_data['websites'] = []
    contact_data['emails'] = []
    contact_data['phones'] = []
    
    if contact_data['linkedin'] == None:
        contact_data['linkedin'] = url
    else:
        if contact_data['linkedin'] != url:
            contact_data['websites'].append(contact_data['linkedin'])
            contact_data['linkedin'] = url

    driver.get(url)
    driver.implicitly_wait(10)

    loc1 = driver.find_elements_by_css_selector('li.inline-block')
    if len(loc1)>0:
        loc_0 = loc1[0].text
        contact_data['location'] = loc_0
        # print(f"Location {contact_data['contact_name']}: {loc_0}")

    if contact_data['company_name'] == None:
        comp = driver.find_elements_by_css_selector('a.pv-top-card--experience-list-item')
        if len(comp)>0:
            cname = comp[0].find_element_by_css_selector('span').text
            contact_data['company_name'] = cname
    
    time.sleep(5)

    if url[-1] == '/': url = url[:-1]

    driver.get(f'{url}/detail/contact-info/')
    driver.implicitly_wait(10)
    
    contact_info = driver.find_elements_by_css_selector(".pv-contact-info__ci-container")
    print(len(contact_info))

    for detail in contact_info:
        try:
            webs = detail.find_elements_by_css_selector('a')
            if webs:
                for elem in webs: 
                    url = elem.get_attribute('href')
                    if url.startswith('mailto:'):
                        email = url.replace('mailto:','').strip()
                        contact_data['emails'].append(email)
                        print(email)
                    else:
                        web_domain = tldextract.extract(url).domain
                        if web_domain != 'linkedin':
                            contact_data['websites'].append(url)
                            print(url)
        except Exception as err:
            print(f"Error parsing href: {err}")

        try:
            telphones = detail.find_elements_by_class_name('t-14 t-black t-normal')
            if telphones:
                for el in telphones:
                    phone = el.text
                    contact_data['phones'].append(phone)
                    print(phone)
        except Exception as err:
            print(f"Error parsing phones: {err}")
            
    return contact_data

def enricher(driver,contact_data):
    crawl_data = contact_data
    linkedin_url = contact_data['linkedin']
    if linkedin_url == None:
        try:
            l_url = googling(driver,contact_data)
            if l_url:
                crawl_data = crawling(driver,l_url,contact_data)
        except Exception as err:
            print(f"Error1: {err}")
    else:
        url_domain = tldextract.extract(linkedin_url).domain
        if url_domain != 'linkedin':
            try:
                l_url = googling(driver,contact_data)
                if l_url:
                    crawl_data = crawling(driver,l_url,contact_data)
            except Exception as err:
                print(f"Error2: {err}")
        else:
            if linkedin_url[-1] == '/': 
                linkedin_url = linkedin_url[:-1]
            linkedin_suffix = linkedin_url.split('/')[-1]
            linkedin_url = f"https://www.linkedin.com/in/{linkedin_suffix}"
            try:
                crawl_data = crawling(driver,linkedin_url,contact_data)
            except Exception as err:
                print(f"Error3: {err}")
    
    return crawl_data