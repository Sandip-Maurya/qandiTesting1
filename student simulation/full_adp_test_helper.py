import time
from selenium.webdriver.common.by import By
import adp_test_helper



def start_test(driver,subject):
    custom_exam_url = "https://app.qandi.com/exam_custom"
    driver.get(custom_exam_url)
    
   
    subject_tab_xp = f'//*[@id="{subject}-tab"]'
    subject_tab = driver.find_element(By.XPATH,subject_tab_xp)
    subject_tab.click()
   
    full_test_el = driver.find_element(By.XPATH,f'//*[@id="{subject}"]/div[1]/div[1]/form/button')
    full_test_el.click()
   
   
    time.sleep(2)
    
    go_for_it_xp = f'//*[@id="goto-exam-btn"]'
   
    go_for_it_el = driver.find_element(By.XPATH,go_for_it_xp)
    go_for_it_el.click()



def get_qid(driver):
    id_xp = f'//*[@id="current_question"]'
    return int(driver.find_element(By.XPATH,id_xp).get_attribute('value'))


def submit_exam(driver):
    submit_btn_xp = f'//*[@id="submitExam"]'
    driver.find_element(By.XPATH,submit_btn_xp).click()
   
    time.sleep(2)
   
    confirmation_xp = f'//*[@id="bt-modal-confirm"]'
    driver.find_element(By.XPATH,confirmation_xp).click()

def get_option_xp(idx,is_first_ques):
    if is_first_ques:
        return f'//*[@id="question_section"]/div[2]/div[2]/div[{idx}]/div/label'
    else:
        return f'//*[@id="question_section"]/div/div[2]/div[2]/div[{idx}]/div/label'

def mark_option(driver,record_df,current_qid,is_first_ques):
    try:
        correct_option_ind = record_df.loc[current_qid, 'corr_opt']
    except:
        correct_option_ind = 4
        print("qid not found")
    oxp = get_option_xp(correct_option_ind,is_first_ques)
    driver.find_element(By.XPATH,oxp).click()

def save_n_next(driver,is_first_ques):
    if is_first_ques:
        save_next_btn_xp = f'//*[@id="question_section"]/div[3]/a[1]'
    else:
        save_next_btn_xp = f'//*[@id="question_section"]/div/div[3]/a[1]'
    driver.find_element(By.XPATH,save_next_btn_xp).click() 

def end_exam_confirm(driver):
    sub_test_btn_xp = f'//*[@id="bt-modal-confirm"]'
    driver.find_element(By.XPATH,sub_test_btn_xp).click()

subjects = ['Physics','Chemistry','Mathematics']
