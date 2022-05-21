from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd
import os, re, time, json, random


mobile = '9910737626'
login_url = 'https://app.qandi.com/login'
mobile_email_xp = '//*[@id="mobile_num"]'
next_btn_xp = '//*[@id="mobile-input-btn"]'
enter_otp_xp = '//*[@id="otp_num"]'
verify_xp = '//*[@id="otp-verify-btn"]'
custom_url = 'https://app.qandi.com/exam_custom'

sub_xp = '//*[@id="Mathematics-tab"]'
save_and_next_xp_f = '//*[@id="question_section"]/div[3]/a[1]'
save_and_next_xp_o = '//*[@id="question_section"]/div/div[3]/a[1]'

wait = 3
prob = 0.9 # for toppers
q_data = pd.read_csv('live_ques_data_for_automation_testing.csv', sep = '|')

# Get browser
def get_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(10)
    return driver


# Login to qandi
def login():
    driver.get(login_url)
    driver.find_element(By.ID, 'mobile_num').send_keys(mobile)
    next_btn_elm = driver.find_element(By.ID, 'mobile-input-btn')
    try:
        next_btn_elm.click()
        enter_otp_elm = driver.find_element(By.ID, 'otp_num')
    except:
        try:
            driver.execute_script("arguments[0].click();", next_btn_elm)
            enter_otp_elm = driver.find_element(By.ID, 'otp_num')
        except:
            print('Not able to login')
    otp = input('Please input otp and then press enter to continue:')
    enter_otp_elm.send_keys(otp)
    verify_elm = driver.find_element(By.ID, 'otp-verify-btn')
    try:
        verify_elm.click()
    except:
        driver.execute_script("arguments[0].click();", verify_elm)
    return


# get Chapter ids
def get_chp_ids():
    driver.get(custom_url)
    driver.find_element(By.XPATH, sub_xp).click()
    pg_src_chp_id = driver.page_source
    time.sleep(1)
    chp_ids = re.findall(r'expand_topic_(\d+)', pg_src_chp_id)
    chp_ids = [int(i) for i in chp_ids]
    return chp_ids


# get Topic Ids from chapter id
def get_topic_ids(chp_id):
    q_data_df = pd.read_csv('q_data.csv')
    topic_ids = q_data_df[q_data_df['chap_id']==chp_id].top_id.unique()
    topic_ids = list(topic_ids)
    return topic_ids


# Get Subject Name from chapter id
def get_subject(chp_id):
    topic_id = get_topic_ids(chp_id)[0]
    topic_df = pd.read_csv('Topic_ID.csv')
    Subject = topic_df[topic_df['Topic ID']==topic_id]['Subject'].unique()[0]
    return Subject


# Select a subject and go to chapter and expand to topics from chapter
def select_sub_tab_and_expand_chp(chp_id):
    # select subject tab
    subject = get_subject(chp_id)
    subject_tab_xp = f'//*[@id="{subject}_btn"]'
    subject_tab_elm = driver.find_element(By.XPATH, subject_tab_xp)
    driver.execute_script("arguments[0].click();", subject_tab_elm)
    
    # expand topic
    chp_xp = f'//*[@id="expand_topic_{chp_id}"]'
    chp_elm = driver.find_element(By.XPATH, chp_xp)
    driver.execute_script("arguments[0].click();", chp_elm)
    
    # retry if not chapter is not expanded
    topic_id = get_topic_ids(chp_id)[0]
    check_elm_xp = f'//*[@id="topic_box_{topic_id}"]/div[3]'
    check_elm = driver.find_element(By.XPATH, check_elm_xp)
    if check_elm.get_attribute('innerText') != 'K\nC\nA\nE\nSELECT':
        driver.execute_script("arguments[0].click();", chp_elm)
    return


# Select topic and start the test
def start_test(topic_id):
    topic_xp = f'//*[@id="chpt_topic_{topic_id}"]'
    try:
        topic_elm = driver.find_element(By.XPATH, topic_xp)
        driver.execute_script("arguments[0].click();", topic_elm)
    except Exception as e:
        print(f"unable to start test :{e}")
        return -1
    take_test_for_sel_topic_xp = '//*[@id="topic_custom_footer"]/button'          
    take_test_for_sel_topic_elm = driver.find_element(By.XPATH, take_test_for_sel_topic_xp)
    driver.execute_script("arguments[0].click();", take_test_for_sel_topic_elm)
    time.sleep(1)
    go_for_it_xp = '//*[@id="goto-exam-btn"]'
    go_for_it_elm = driver.find_element(By.XPATH, go_for_it_xp)
    driver.execute_script("arguments[0].click();", go_for_it_elm)
    return


# Get current question id
def get_curr_q_id():
    curr_q_xp = '//*[@id="current_question"]'
    curr_q_elm = driver.find_element(By.XPATH, curr_q_xp)
    curr_q_id = curr_q_elm.get_attribute('value')    
    return int(curr_q_id)


# Select an option and clicks the 'save and next' button
def do_question(o_xps, save_and_next_xp, wait):
    # choose option
    for o_xp in o_xps:
        o_xp_elm = driver.find_element(By.XPATH, o_xp)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", o_xp_elm)
    
    # click save and next after wait time is over
    time.sleep(wait)
    save_and_next_elm = driver.find_element(By.XPATH, save_and_next_xp)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", save_and_next_elm)
    return


# Get correct options based on probability from question id 
def get_corr_options(q_id, prob):
    ans_text = q_data[q_data['question_id']==q_id]['answers'].values[0]
    ans_text_dict = json.loads(ans_text)
    corr_options = list(ans_text_dict.keys())
    corr_options = [int(i) for i in corr_options]
    incorr_options = [i for i in range(1,5) if i not in corr_options]
    if random.random() > prob:
        corr_options[0] = incorr_options[0]
    return corr_options


# Attempt Topic test. It completes all the questions in one session. 
def do_topic_test():
    # Do first question
    curr_q_id = get_curr_q_id()
    corr_options = get_corr_options(curr_q_id, prob)
    count = 0
    o_xps = []
    for corr_option in corr_options:
        o_xp_f = f'//*[@id="question_section"]/div[2]/div[2]/div[{corr_option}]/div/label'
        o_xps.append(o_xp_f)
    do_question(o_xps, save_and_next_xp_f, wait)
    count += 1
    print(f'No. of questions done: {count}')
    # Do other questions
    sub_test_xp = '//*[@id="bt-modal-confirm_over"]'
    sub_test_elm = driver.find_element(By.XPATH, sub_test_xp)
    test_end_condition = sub_test_elm.get_attribute('innerText')

    while test_end_condition != 'SUBMIT TEST':
        o_xps = []
        curr_q_id = get_curr_q_id()
        corr_options = get_corr_options(curr_q_id, prob)
        for corr_option in corr_options:
            o_xp_o = f'//*[@id="question_section"]/div/div[2]/div[2]/div[{corr_option}]/div/label'
            o_xps.append(o_xp_o)

        time.sleep(1)
        do_question(o_xps, save_and_next_xp_o, wait)
        count += 1
        print(f'No. of questions done: {count}')
        sub_test_elm = driver.find_element(By.XPATH, sub_test_xp)
        test_end_condition = sub_test_elm.get_attribute('innerText')

    time.sleep(1)
    driver.execute_script("arguments[0].click();", sub_test_elm)
    return 
