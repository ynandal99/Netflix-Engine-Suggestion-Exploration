# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 12:07:19 2022

@author: Nandal
"""

import datetime
from datetime import timedelta
from selenium import webdriver
from time import localtime, strftime
import time
import sys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tkinter import ttk
from ttkthemes import ThemedTk
import tkinter as tk
import pyttsx3
from playsound import playsound
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import pandas as pd
from tkinter import Canvas
import zipfile
import urllib.request
import os
import re
import requests
import json

homedir = os.getcwd()

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

engine = pyttsx3.init()
engine.setProperty('rate', 165)        

driver.get(r'https://www.netflix.com/ca/Login')
driver.maximize_window()   

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

engine.say('NOW, Login into netflix please!')
engine.runAndWait()

cnt=0

# fun to click on search icon and send search text
def search(text):
    global cnt
    cnt+=1
    srch_btn = driver.find_element_by_xpath('//*[@class="icon-search"]')
    srch_btn.click()
    srch_field = driver.find_element_by_xpath('//*[@class="searchInput"]')
    srch_field.click()
    srch_in_field = driver.find_element_by_xpath('//*[@name="searchInput"]')
    srch_in_field.click()    
    try:
        if srch_in_field.is_displayed():
            srch_in_field.clear()    
            srch_in_field.send_keys(text)
    except:
        if cnt<=3:
            search(text)

search("Murdoch Mysteries")

# wait for slow loads

time.sleep(2)

# save images and titles

srch_results = driver.find_elements_by_xpath('//*[@class="title-card-container css-0"]') 

master_json = {}

for y in srch_results:
    x = y.get_attribute('innerHTML')
    
    x = x.replace(r'%22',r'"')
    x = x.replace(r'%7D',r'}')
    x = x.replace(r'%7B',r'{')
    x = x.replace(r'%7C',r'|')
    x = x.replace(r'%20',r' ')
    
    json_info = json.loads(re.findall('"{.*?}"', x)[0][1:-1])
    master_json.update(json_info)
    img_url = y.find_element_by_xpath('//*[@class="ptrack-content"]').find_element_by_tag_name('img').get_attribute('src')
    img_name = y.text
    img_name = re.sub(r'[":\-();*!@#$%^&=`~+,.<>?/\n"]', "_",img_name)
    print(img_name)
# =============================================================================
#     if f'{img_name}.jpg' not in os.listdir():
#         urllib.request.urlretrieve(img_url, f'{img_name}.jpg')
# =============================================================================

cols = []

tn_dict = {}


for s in srch_results:
    s.click()
    time.sleep(2)
    video = WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="vjs-tech"]')))
    video_url = video.get_property('src')    
    videoname = driver.title
    videoname = re.sub(r'[":\-();*!@#$%^&=`~+,.<>?/\n"]', "_",videoname)
    if f'{ctr}_{videoname}.mp4' not in os.listdir():
        urllib.request.urlretrieve(video_url, f'{ctr}_{videoname}.mp4')


engine.say('All videos downloaded. Enjoy')
engine.runAndWait()

# Make folder 

try:
    folder_name = WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="clamp-1 t-16 t-bold t-white "]'))).text
    folder_name = re.sub(r'[":\-();*!@#$%^&=`~+,.<>?/\n"]', "_",folder_name)
except:
    driver.refresh() 
    time.sleep(3)
    folder_name = WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="clamp-1 t-16 t-bold t-white "]'))).text
    folder_name = re.sub(r'[":\-();*!@#$%^&=`~+,.<>?/\n"]', "_",folder_name)
    
try:
    os.chdir(homedir)
    os.makedirs(folder_name)
    os.chdir(folder_name)
except:
    os.chdir(homedir)
    os.chdir(folder_name)
    print("Folder Already exists, vidoes may be overwritten")

ctr = 0