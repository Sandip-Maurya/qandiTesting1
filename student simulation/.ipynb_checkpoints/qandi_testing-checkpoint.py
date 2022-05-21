#!/usr/bin/env python
# coding: utf-8

# In[8]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time, datetime, smtplib, random
from email.message import EmailMessage
import re
import time
import pandas as pd


# path = "/usr/bin/chromedriver" 
path = r'C:\Users\USER\Desktop\chromedriver.exe'

ser = Service(path)
chromeOptions = Options()
chromeOptions.add_argument('--no-sandbox')
# chromeOptions.add_argument('--headless')

driver = webdriver.Chrome(service = ser,  options=chromeOptions)


# In[116]:


import os


# In[9]:


# xpaths and other data

login_url = 'https://app.qandi.com/login'
email = '9560795635'
email_xp = '//*[@id="mobile_num"]'
next_btn_xp = '//*[@id="mobile-input-btn"]'
custom_exam_url = 'https://app.qandi.com/exam_custom'

# For first question
o1_xp_f = '//*[@id="question_section"]/div[2]/div[2]/div[1]/div/label'
o2_xp_f = '//*[@id="question_section"]/div[2]/div[2]/div[2]/div/label'
o3_xp_f = '//*[@id="question_section"]/div[2]/div[2]/div[3]/div/label'
o4_xp_f = '//*[@id="question_section"]/div[2]/div[2]/div[4]/div/label'
o_xps_f = [o1_xp_f, o2_xp_f, o3_xp_f, o4_xp_f]
save_and_next_xp_f = '//*[@id="question_section"]/div[3]/a[1]'

# For other questions
o1_xp_o = '//*[@id="question_section"]/div/div[2]/div[2]/div[1]/div/label'
o2_xp_o = '//*[@id="question_section"]/div/div[2]/div[2]/div[2]/div/label'
o3_xp_o = '//*[@id="question_section"]/div/div[2]/div[2]/div[3]/div/label'
o4_xp_o = '//*[@id="question_section"]/div/div[2]/div[2]/div[4]/div/label'
o_xps_o = [o1_xp_o, o2_xp_o, o3_xp_o, o4_xp_o]

# other xpaths
take_test_for_sel_topic_xp = '//*[@id="topic_custom_footer"]/button'
go_for_it_xp = '//*[@id="goto-exam-btn"]'
phy_xp = '//*[@id="Physics-tab"]'
chem_xp = '//*[@id="Chemistry-tab"]'
math_xp = '//*[@id="Mathematics-tab"]'
save_and_next_xp_o = '//*[@id="question_section"]/div/div[3]/a[1]'

sub_test_xp = '//*[@id="bt-modal-confirm_over"]'


# In[10]:


# Login manually 
# skm4985 id is used for testing. Mobile number is random

driver.get(login_url)
time.sleep(1)

driver.find_element(By.XPATH, email_xp).send_keys(email)
time.sleep(1)

driver.find_element(By.XPATH, next_btn_xp).click()


# In[4]:


# Enter otp and sign in step


# In[11]:


# Load question_data
q_data_df = pd.read_csv('q_data.csv')
topic_df = pd.read_csv('Topic_ID.csv')
q_data_df[:2]


# In[12]:


topic_df[:2]


# In[71]:


def get_chp_ids(sub_xp):
    
    driver.get(custom_exam_url)
    time.sleep(0.5)
    driver.find_elements(By.XPATH, sub_xp)[0].click()
    time.sleep(1)
    pg_src_chp_id = driver.page_source
    chp_ids = re.findall(r'expand_topic_(\d+)', pg_src_chp_id)
    chp_ids = [int(i) for i in chp_ids]
    return chp_ids


# In[72]:


def get_topic_ids(chp_id):
    # get subject and topic_ids from chapter id (chp_id)
    topic_ids = q_data_df[q_data_df['chap_id']==chp_id].top_id.unique()
    Subject = topic_df[topic_df['Topic ID']==topic_ids[0]].Subject.values[0]
    # print(Subject)
    
    tab_xp = f'//*[@id="{Subject}-tab"]'
    tab_elm = driver.find_elements(By.XPATH, tab_xp)[0]
    driver.execute_script("arguments[0].click();", tab_elm)
    
    chp_xp = f'//*[@id="expand_topic_{chp_id}"]'
    chp_elm = driver.find_elements(By.XPATH, chp_xp)[0]
    driver.execute_script("arguments[0].click();", chp_elm)

    return topic_ids


# In[ ]:


def start_test_and_get_id_of_first_q(topic_id):
    # Select topic and start the test
    topic_xp = f'//*[@id="chpt_topic_{topic_id}"]'
    time.sleep(2)
    
    while True:
        try:
            topic_elm = driver.find_elements(By.XPATH, topic_xp)[0]
            driver.execute_script("arguments[0].click();", topic_elm)
            break
        except Exception as e:
            print(e)
            print("invalid topic id")
            return -1
                
    take_test_for_sel_topic_elm = driver.find_elements(By.XPATH, take_test_for_sel_topic_xp)[0]
    driver.execute_script("arguments[0].click();", take_test_for_sel_topic_elm)

    # Exam Starts now
    time.sleep(1)
    go_for_it_elm = driver.find_elements(By.XPATH, go_for_it_xp)[0]
    driver.execute_script("arguments[0].click();", go_for_it_elm)
    
    # Get current question id
    q_id_pg_src = driver.page_source
    curr_q_id = re.findall(r'id="current_question" value="(\d+)"', q_id_pg_src)[0]
    curr_q_id  = int(curr_q_id)
    return curr_q_id


# In[ ]:





# In[74]:


def choose_an_option_and_record(curr_q_id, record_df):
    curr_q_data = q_data_df[q_data_df['q_id']==curr_q_id].iloc[0,:].tolist()
    Response_data = [curr_q_data[1], True]
    curr_q_record = curr_q_data + Response_data
    record_df.loc[curr_q_id,:] = curr_q_record
    return record_df
# choose_an_option_and_record(curr_q_id, record_df)


# In[75]:


def do_first_questions(o_xp):
    o_xp_elm = driver.find_elements(By.XPATH, o_xp)[0]
    driver.execute_script("arguments[0].click();", o_xp_elm)
    time.sleep(1)
    
    save_and_next_elm = driver.find_elements(By.XPATH, save_and_next_xp_f)[0]
    driver.execute_script("arguments[0].click();", save_and_next_elm)
    time.sleep(0.5)
    return 


# In[76]:


def do_other_questions(o_xp):
    o_xp_elm = driver.find_elements(By.XPATH, o_xp)[0]
    driver.execute_script("arguments[0].click();", o_xp_elm)
    time.sleep(1)
    
    save_and_next_elm = driver.find_elements(By.XPATH, save_and_next_xp_o)[0]
    driver.execute_script("arguments[0].click();", save_and_next_elm)
    time.sleep(0.5)
    return 


# In[129]:


def make_csv(record_df):
    topic_id = record_df.iloc[0,3]
    Subject = topic_df[topic_df['Topic ID']==topic_id].Subject.values[0]
    Topic = topic_df[topic_df['Topic ID']==topic_id].Topic.values[0]
    
    remove_symbols = r'\/:*?"<>|'
    for symbol in remove_symbols:
        Topic = Topic.replace(symbol, ',')
    file_name = f'botTestOutput/{Subject[0]}_{Topic}.csv'
    
    driver.save_screenshot(os.path.join(os.getcwd(),'botTestOutput',f'{Subject[0]}_{Topic}.png'))

    
    record_df.to_csv(file_name, index=False)
    


# In[133]:


def attempt_topic_test(topic_id):
    curr_q_id = start_test_and_get_id_of_first_q(topic_id)
    
    if curr_q_id == -1:
        return pd.DataFrame()
    
    columns = 'q_id corr_opt diff_lev top_id chap_id opt_chosen isResponseCorrect'.split(' ')
    record_df = pd.DataFrame(columns = columns)
    record_df = choose_an_option_and_record(curr_q_id, record_df)
    correct_option_ind = record_df.loc[curr_q_id, 'corr_opt']-1
    o_xp = o_xps_f[correct_option_ind]

    do_first_questions(o_xp)
    
    count = 1

    while True:
        try:
            # Do the questions till all questions in the topic are exhausted
            time.sleep(1)
            q_id_pg_src = driver.page_source
            curr_q_id = re.findall(r'id="current_question" value="(\d+)"', q_id_pg_src)[0]
            curr_q_id =int(curr_q_id)
            record_df = choose_an_option_and_record(curr_q_id, record_df)
            correct_option_ind = record_df.loc[curr_q_id, 'corr_opt']-1
            o_xp = o_xps_o[correct_option_ind]
            do_other_questions(o_xp)
            
            end_exam_xp = '//*[@id="endExam"]'
            
            count += 1
            
            # this is used for debugging purposes
            end_test_early = False

            try:
                end_exam_elm = driver.find_elements(By.XPATH, end_exam_xp)[0]
                test_condition = end_exam_elm.value_of_css_property('display')
                
                # 
                if test_condition!='none' or end_test_early:
                    print('No more questions available.')
                    break
            except Exception as e:
                #print(e)
                pass
            
        except:
            print('Break due to other reason')
            break
    return record_df


# In[134]:


# To get all the chp_ids we need any subject_tab_xp and call get_chp_ids function 
chp_ids = get_chp_ids(math_xp)


# In[135]:


# Start the topic test one by one

driver.get(custom_exam_url)
time.sleep(1)
for chp_id in chp_ids[0:200]:
    print("currently testing chapter ID : {}".format(chp_id))
    topic_ids = get_topic_ids(chp_id)
    # print(topic_ids)
    time.sleep(1)
    # topic_ids = list(topic_ids)
    for topic_id in topic_ids:
        #get_topic_ids(chp_id)
        record_df = attempt_topic_test(topic_id)
        
        if record_df.empty:
            continue
            
        print("test attempted sucessfully")
        
        # submit the test 
        sub_test_elm = driver.find_elements(By.XPATH, sub_test_xp)[0]
        driver.execute_script("arguments[0].click();", sub_test_elm)
        
        time.sleep(2)

        


        # Make csv for the current topic
        make_csv(record_df)

        driver.get(custom_exam_url)
        time.sleep(1)
        get_topic_ids(chp_id)        
        
        
        print(f'Test completed for the topic id: {topic_id}')

print('Done')
record_df


# In[101]:


driver.save_screenshot(f'botTestOutput/test.png')


# In[103]:


file_name


# In[ ]:




