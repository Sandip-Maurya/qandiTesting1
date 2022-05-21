from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from datetime import datetime

# returns the driver object
def get_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # set implicit wait for 10s
    driver.implicitly_wait(10)

    return driver

# save screenshots with the given tag in the given folder
def save_screenshot(driver,folder,tag):
    now = datetime.now() # current date and time
    date_time = now.strftime("%m %d %Y-%H %M %S")
    return driver.save_screenshot(os.path.join(os.getcwd(),folder,f'{tag}_{date_time}.png'))


# makes a csv record of the current session
def make_csv(driver,record_df,qdata):
    _ , topic_df = qdata.get()

    topic_id = record_df.iloc[0,3]
    Subject = topic_df[topic_df['Topic ID']==topic_id].Subject.values[0]
    Topic = topic_df[topic_df['Topic ID']==topic_id].Topic.values[0]
    
    remove_symbols = r'\/:*?"<>|'
    for symbol in remove_symbols:
        Topic = Topic.replace(symbol, ',')
    file_name = f'botTestOutput/{Subject[0]}_{Topic}.csv'
    
    driver.save_screenshot(os.path.join(os.getcwd(),'botTestOutput',f'{Subject[0]}_{Topic}.png'))

    
    record_df.to_csv(file_name, index=False)