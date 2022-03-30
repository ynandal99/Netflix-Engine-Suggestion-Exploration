# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 12:07:19 2022

@author: Nandal
"""

from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pyttsx3
import pandas as pd
import zipfile
import urllib.request
import os
import re
import requests
import json

homedir = os.getcwd()

# This try except checks if chromedriver is present or not, if not, latest one is fetched based on user input of chrome version
try:
  driver = webdriver.Chrome(executable_path=r'chromedriver.exe')
except:
  # get a self updating webdriver
  print('*'*45)
  print('*'*45)
  print(''*45)
  print('Please wait, updating chrome driver, just go to your browser and paste the chrome version (for e.g. - 99.0.4197.75) and hit enter\n')
  ans = 'Y'
  while ans == 'Y':
    url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_'
    url_file = 'https://chromedriver.storage.googleapis.com/'
    file_name = 'chromedriver_win32.zip'
    version = input('Now Enter Current Chrome Browser Version from :(3 dots) -> Help -> About Google Chrome: ')
    version_test = version.split('.')[:3]
    version_test = '.'.join(version_test)  
    version_response = requests.get(url + version_test)
    if 'Error' not in version_response.text:
        file = requests.get(url_file + version_response.text + '/' + file_name)
        with open(file_name, "wb") as code:
            code.write(file.content)
        print('\nSuccessfully downloaded new version, now extracting zip.....')
        with zipfile.ZipFile(file_name, 'r') as zip:
            # printing all the contents of the zip file
            zip.printdir()
          
            # extracting all the files
            print('\nExtracting all the files now...')
            zip.extractall()
            print('*'*45)
            print('*'*45)            
            print('\nDone! Re-starting program!! Please wait...')
            print('*'*45)
            print('*'*45)                
            driver = webdriver.Chrome(executable_path=r'chromedriver.exe')
        ans = 'n'
    else:
      answer = input('\nDid you enter the version correctly, without any leading or trailing spaces? Try again?: [Y/N] ?')
      if answer == '':
        ans = 'Y'
      else:
        ans = answer[0].upper()

# Initialize speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 165)        

# Load website
driver.get(r'https://www.netflix.com/ca/Login')
driver.maximize_window()   

engine.say("Please login then answer the following questions only in specified format")
engine.runAndWait()

# =============================================================================
# login_btn = driver.find_element_by_xpath('//*[@id="id_userLoginId"]')
# login_btn.click()
# login_btn.send_keys(r"@gmail.com"+ Keys.ENTER)   
# 
# ms_pass = WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="passwordInput"]')))
# ms_pass.send_keys(r"" + Keys.ENTER)
# 
# stay_signed_in_btn = driver.find_element_by_xpath('//*[@id="idBtn_Back"]')
# stay_signed_in_btn.click()
# =============================================================================

uname = str(input('Please enter Netflix viewer Name:\n'))
uage = int(input('Please enter Netflix viewer Age (as integer):\n'))
ugender = str(input('Please enter Netflix viewer Gender (M/F only):\n'))

# Specify search depth (the more the depth, more times page will be scrolled to load more results), default = 1, max=5
flag = True
while flag:
    search_depth = int(input("Specify search depth or page scrolls to include more results bw 1 to 7: \n"))
    if search_depth <=7 and search_depth>=1:
        flag = False
    else:
        print("Enter valid input from 1 to 5")
        
engine.say('Beginning Search! Make Chrome window active on screen and Do not move your mouse or press any keys until script finishes.')
engine.runAndWait()

master_json = {}


text_list = pd.read_csv('searchTerms.csv')
text_list = text_list['terms'].to_list()
        
# fun to click on search icon and send search text (pass a list in here)
def search(text_list):
    global master_json, driver, search_depth
    for text in text_list:
        cnt=0
        local_json = {}
        driver.get(r'https://www.netflix.com/browse')
        srch_btn = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="icon-search"]')))
        srch_btn.click()
        srch_field = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="searchInput"]')))
        srch_field.click()
        srch_in_field = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@name="searchInput"]')))
        srch_in_field.click()    
        try:
            if srch_in_field.is_displayed():
                srch_in_field.clear() 
                time.sleep(1)
                srch_in_field.send_keys(text + Keys.ENTER)
        except:
            cnt +=1
            if cnt<=3:
                search(text)
        
        #Deep search params
        for i in range(search_depth):
            body = driver.find_element_by_css_selector('body')
            body.send_keys(Keys.PAGE_DOWN + Keys.PAGE_DOWN + Keys.PAGE_DOWN)        
            # wait for slow loads        
            time.sleep(3)
        
        # save images and titles
        
        srch_results = driver.find_elements_by_xpath('//*[@class="title-card"]')
        
        global homedir
        folder_name = text
        try:
            os.chdir(homedir)
            os.makedirs(folder_name)
            os.chdir(folder_name)
        except:
            os.chdir(homedir)
            os.chdir(folder_name)
            print("Folder Already exists, media may be overwritten")    
        for y in srch_results:      
            x = y.get_attribute('innerHTML')
            hov = ActionChains(driver).move_to_element(y)
            hov.perform()
            try:
                try:
                    maturity_number = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="maturity-number"]'))).text
                except:
                    maturity_number = ''
                try:
                    match_score = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="match-score"]'))).text[:3]
                except:
                    match_score = ''
                try:
                    WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="evidence-text"]')))
                    genre = [e.text for e in driver.find_elements_by_xpath('//*[@class="evidence-text"]')]
                    genre = ','.join(genre)
                except:
                    genre = '' 
                try:
                    duration = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="duration"]'))).text
                except:
                    duration=''
                body.send_keys(Keys.ESCAPE)
            except:
                body.send_keys(Keys.ESCAPE)
                hov.perform()   
                try:
                    maturity_number = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="maturity-number"]'))).text
                except:
                    maturity_number = ''
                try:
                    match_score = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="match-score"]'))).text[:3]
                except:
                    match_score = ''
                try:
                    WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="evidence-text"]')))
                    genre = [e.text for e in driver.find_elements_by_xpath('//*[@class="evidence-text"]')]
                    genre = ','.join(genre)
                except:
                    genre = ''             
                try:
                    duration = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="duration"]'))).text
                except:
                    duration=''
                body.send_keys(Keys.ESCAPE)
    
            x = x.replace(r'%22',r'"')
            x = x.replace(r'%7D',r'}')
            x = x.replace(r'%7B',r'{')
            x = x.replace(r'%7C',r'|')
            x = x.replace(r'%20',r' ')
            
            img_url = re.findall('src=.*?" ', x)[0][5:-2]
            img_name = y.text
            json_info = json.loads(re.findall('"{.*?}"', x)[0][1:-1])
            json_info['match_score'] = match_score
            json_info['maturity_number'] = maturity_number
            json_info['duration'] = duration            
            json_info['genre'] = genre        
            local_json[img_name] = json_info
            img_name = re.sub(r'[":|\-();*!@#$%^&=`~+,.<>?/\n"]', "_",img_name)
            if f'{img_name}.jpg' not in os.listdir():
                urllib.request.urlretrieve(img_url, f'{img_name}.jpg')
        #update master json
        master_json[text] = local_json
    
    rows = []
    cols = []
      
    # appending rows
    for k,v in master_json.items():        
        for m,n in v.items():
            tempr = []
            for o,p in n.items():
                tempr.append(p)
                if o not in cols:
                    cols.append(o)
            tempr.extend([k,m,uname,uage,ugender])
            rows.append(tempr)
        
    cols.append('SearchText')
    cols.append('SearchResults')
    cols.append('UserName')
    cols.append('UserAge')
    cols.append('UserGender')
      
    # using data frame
    df = pd.DataFrame(rows,columns=cols)
    # ordering columns properly
    cols = [
             'SearchText',
             'SearchResults',        
             'rank',         
             'match_score',
             'duration',
             'genre',
             'maturity_number',         
             'UserName',
             'UserAge',
             'UserGender',        
             'list_id',
             'location',
             'request_id',
             'row',
             'track_id',
             'video_id',
             'image_key',
             'supp_video_id',
             'lolomo_id',
             'maturityMisMatchEdgy',
             'maturityMisMatchNonEdgy',
             'titleInformationDensity',
             'titleInformationDensityExplored',
             'napaRequestId',
             'appView',
             'usePresentedEvent'
    ]
    
    df = df[cols]
    #Fix rank starting from zero
    df['rank'] += 1
    df = df.set_index('SearchText')
    cur_time = time.ctime()
    cur_time = cur_time.replace(':','_')
    os.chdir(homedir)
    df.to_csv(f'SearchResults_{cur_time}.csv',index=True)

# send search items list to function
search(text_list)

    
engine.say('All results published. Enjoy')
engine.runAndWait()
