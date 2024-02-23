from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

user = "gpranam@gmail.com"
password = "goyal@1111"

def check_PCR():
    
    driver = webdriver.Chrome()
    driver.get('https://theautotrender.com/login')
    
    try:
        driver.find_element(By.ID, 'mui-1').send_keys(user)
        driver.find_element(By.ID, 'mui-2').send_keys(password)
        driver.find_element(By.CLASS_NAME, 'PrivateSwitchBase-input').click()
        driver.find_element(By.CLASS_NAME, 'MuiButton-root').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div[5]/div[2]/div/div[2]/div/div/div[6]/div/div[2]/div/div/table/thead/tr[1]/th/div/div[1]/button[1]'))).click()
        
        cell1 = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[5]/div[2]/div/div[2]/div/div/div[6]/div/div[2]/div/div/table/tbody/tr[1]/td[3]')
        cell1 = cell1.text
        cell2 = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[5]/div[2]/div/div[2]/div/div/div[6]/div/div[2]/div/div/table/tbody/tr[2]/td[3]')
        cell2 = cell2.text

        return cell1, cell2
    
    except Exception as e:
        print(f"An error occurred: {e}")
   
    finally:
        driver.quit()