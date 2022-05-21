from selenium import webdriver
from selenium.webdriver.common.by import By
import adp_test_helper
import full_adp_test_helper
import utils
from QData import QData
import time,os
import pandas as pd
from datetime import datetime


class Student:
    def __init__(self,driver:webdriver,email:str) -> None:
        self.email = email
        self.driver = driver

    def signup():
        pass
    
    def login(self):
        try:
            login_url = 'https://app.qandi.com/login'
            email_xp = '//*[@id="mobile_num"]'
            next_btn_xp = '//*[@id="mobile-input-btn"]'

            self.driver.get(login_url)

            # fill in the email and click
            self.driver.find_element(By.XPATH, email_xp).send_keys(self.email)
            self.driver.find_element(By.XPATH, next_btn_xp).click()
        except Exception:
            pass
  
    def take_adp_test(self,driver:webdriver,qdata:QData,prob:float): 
        i = 0

        chp_ids = adp_test_helper.get_chp_ids(driver)
        for chp_id in chp_ids:
            i += 1    
            print(f"currently on chapter id : {chp_id} , iteration : {i}")
            topic_ids = adp_test_helper.get_topic_ids(qdata,chp_id)
            _ , topic_df = qdata.get()
            subject = topic_df[topic_df['Topic ID']==topic_ids[0]].Subject.values[0]

           
            for topic_id in topic_ids:
                try:
                    driver.get('https://app.qandi.com/exam_custom')
                    adp_test_helper.select_sub_tab_and_expand_chp(driver, subject , chp_id)
                    has_test_started = adp_test_helper.start_test(driver,topic_id)
                    if has_test_started == -1:
                        continue
                    fq_id = adp_test_helper.click_go_for_it_and_get_id_of_first_q(driver)

                    record_df = adp_test_helper.attempt_topic_test(driver,qdata,topic_id,chp_id,fq_id)

                    time.sleep(2.5)

                    # Make csv for the current topic
                    utils.make_csv(driver,record_df,qdata)
        
                
                    print(f'Test completed for the topic id: {topic_id}')
                except KeyboardInterrupt:
                    # log the error
                    break

    def take_full_adp_test(self,driver:webdriver,sub:str,qdata:QData):
        full_adp_test_helper.start_test(driver,sub)
        time.sleep(4)
        columns = 'q_id corr_opt diff_lev top_id chap_id opt_chosen isResponseCorrect'.split(' ')
        record_df = pd.DataFrame(columns = columns)
        
        for i in range(30):
            try:
                current_qid = full_adp_test_helper.get_qid(driver)
                print(current_qid)

                record_df = adp_test_helper.choose_an_option_and_save_record(qdata,current_qid,record_df)
                full_adp_test_helper.mark_option(driver,record_df,current_qid,i==0)
                full_adp_test_helper.save_n_next(driver,i==0)
                time.sleep(1.5)
            except:
                print('something went wong')
            
        full_adp_test_helper.end_exam_confirm(driver)

    def take_full_body_scan(self,prob):
        pass

    def take_mock_test(self,driver:webdriver,qdata):
        driver.get('https://app.qandi.com/adaptive_exam')

        time.sleep(5)

        # click go for it and start the exam
        go_for_it_xp = f'//*[@id="goto-exam-btn"]'  
        go_for_it_el = driver.find_element(By.XPATH,go_for_it_xp)
        go_for_it_el.click()

        columns = 'q_id corr_opt diff_lev top_id chap_id opt_chosen isResponseCorrect'.split(' ')
        record_df = pd.DataFrame(columns = columns)
            
        for i in range(75+1):
            try:
                current_qid = full_adp_test_helper.get_qid(driver)

                record_df = adp_test_helper.choose_an_option_and_save_record(qdata,current_qid,record_df)
                full_adp_test_helper.mark_option(driver,record_df,current_qid,i==0)
                full_adp_test_helper.save_n_next(driver,i==0)
                time.sleep(1.5)
            except:
                print(f'something went wong on question : {i}')
        
        # save a csv record of the test
        now = datetime.now() # current date and time
        date_time = now.strftime("%m %d %Y-%H %M %S")
        file_name = os.path.join(os.getcwd(),f'mock_test/{date_time}.csv')
        record_df.to_csv(file_name,index=False)

        full_adp_test_helper.end_exam_confirm(driver)


        