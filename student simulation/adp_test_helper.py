from selenium import webdriver
from selenium.webdriver.common.by import By
import re,time
import pandas as pd
import utils

custom_exam_url = 'https://app.qandi.com/exam_custom'

# xpaths for various elements

################################################################################

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

################################################################################


# first question has a slightly differnet HTML structure
def do_first_question(driver,o_xp):

    # option xpath
    o_xp_elm = driver.find_elements(By.XPATH, o_xp)[0]
    driver.execute_script("arguments[0].click();", o_xp_elm)
    
    # save and next element
    save_and_next_elm = driver.find_elements(By.XPATH, save_and_next_xp_f)[0]
    driver.execute_script("arguments[0].click();", save_and_next_elm)

def do_other_questions(driver,o_xp):
    for option_xpath in o_xp:
        # select the option
        o_xp_elm = driver.find_elements(By.XPATH, option_xpath)[0]
        driver.execute_script("arguments[0].click();", o_xp_elm)

        time.sleep(0.5)
        
    time.sleep(2)
        
    # go to next question
    save_and_next_elm = driver.find_elements(By.XPATH, save_and_next_xp_o)[0]
    driver.execute_script("arguments[0].click();", save_and_next_elm)



# get a list of all chapter ids
def get_chp_ids(driver):
    sub_xp = math_xp # can do it for any subject
    driver.get(custom_exam_url)
    driver.find_elements(By.XPATH, sub_xp)[0].click()
    pg_src_chp_id = driver.page_source
    chp_ids = re.findall(r'expand_topic_(\d+)', pg_src_chp_id)
    chp_ids = [int(i) for i in chp_ids]
    return chp_ids

def get_topic_ids(qdata,chp_id):
    q_data_df , topic_df = qdata.get()

    # get topic_ids from chapter id (chp_id)
    topic_ids = q_data_df[q_data_df['chap_id']==chp_id].top_id.unique()

    return topic_ids

def select_sub_tab_and_expand_chp(driver,subject,chp_id):
    # select subject tab     
    tab_xp = f'//*[@id="{subject}-tab"]'
    tab_elm = driver.find_elements(By.XPATH, tab_xp)[0]
    driver.execute_script("arguments[0].click();", tab_elm)
    
    # expand topic
    chp_xp = f'//*[@id="expand_topic_{chp_id}"]'
    chp_elm = driver.find_elements(By.XPATH, chp_xp)[0]
    driver.execute_script("arguments[0].click();", chp_elm)

def start_test(driver,topic_id):
     # Select topic and start the test
    topic_xp = f'//*[@id="chpt_topic_{topic_id}"]'
    
    try:
        topic_elm = driver.find_elements(By.XPATH, topic_xp)[0]
        driver.execute_script("arguments[0].click();", topic_elm)
    except Exception as e:
        print(f"unable to start test :{e}")
        return -1
                
    take_test_for_sel_topic_elm = driver.find_elements(By.XPATH, take_test_for_sel_topic_xp)[0]
    driver.execute_script("arguments[0].click();", take_test_for_sel_topic_elm)

def click_go_for_it_and_get_id_of_first_q(driver):
    # Click on go for it
    go_for_it_elm = driver.find_elements(By.XPATH, go_for_it_xp)[0]
    driver.execute_script("arguments[0].click();", go_for_it_elm)
    time.sleep(0.5)

    # Get current question id
    q_id_pg_src = driver.page_source
    curr_q_id = re.findall(r'id="current_question" value="(\d+)"', q_id_pg_src)[0]
    curr_q_id  = int(curr_q_id)
    return curr_q_id


def choose_an_option_and_save_record(qdata,curr_q_id, record_df):
    try:
        q_data_df , _ = qdata.get()

        curr_q_data = q_data_df[q_data_df['q_id']==curr_q_id].iloc[0,:].tolist()
        Response_data = [curr_q_data[1], True]
        curr_q_record = curr_q_data + Response_data
        record_df.loc[curr_q_id,:] = curr_q_record
        return record_df
    except Exception as e:
        print(f"failed : {e}")
def get_qid_from_page_src(driver):
    q_id_pg_src = driver.page_source
    curr_q_id = re.findall(r'id="current_question" value="(\d+)"', q_id_pg_src)[0]
    return int(curr_q_id)

def extract_options(s):
    options = []
    for opt in s.split(","):
        options.append(int(re.findall("\d",opt)[0]))
    return options
    

def attempt_topic_test(driver,qdata,topic_id,chp_id,curr_q_id):
    
    columns = 'q_id corr_opt diff_lev top_id chap_id opt_chosen isResponseCorrect'.split(' ')
    record_df = pd.DataFrame(columns = columns)
    record_df = choose_an_option_and_save_record(qdata,curr_q_id, record_df)
    print('cross')
    #correct_option_ind = record_df.loc[curr_q_id, 'corr_opt']-1
    correct_option_ind = 3
    o_xp = o_xps_f[correct_option_ind]
    
    try:
        do_first_question(driver,o_xp)
    except:
        print('something went wrong while attempting the first question !')
        return
    
    count = 1

    while True:
        try:
            # Do the questions till all questions in the topic are exhausted
            time.sleep(1)
            q_id_pg_src = driver.page_source
            curr_q_id = re.findall(r'id="current_question" value="(\d+)"', q_id_pg_src)[0]
            curr_q_id =int(curr_q_id)
            
            record_df = choose_an_option_and_save_record(qdata,curr_q_id, record_df)
            print("cross-2")
            # working version for single correct
            # correct_option_ind = record_df.loc[curr_q_id, 'corr_opt']-1
            # o_xp = o_xps_o[correct_option_ind]

            # do_other_questions(driver,o_xp)

            correct_option_str = record_df.loc[curr_q_id, 'corr_opt']
            print(correct_option_str)
            correct_option_indices = extract_options(correct_option_str)
            print(correct_option_indices)

            o_xp = []

            for opt in correct_option_indices: 
                o_xp.append(o_xps_o[opt-1])

            do_other_questions(driver,o_xp)




            
            end_exam_xp = '//*[@id="endExam"]'
            
            count += 1
            
            # this is used for debugging purposes
            end_test_early = (count==100)

            try:
                end_exam_elm = driver.find_elements(By.XPATH, end_exam_xp)[0]
                test_condition = end_exam_elm.value_of_css_property('display')
                
                
                if test_condition!='none' or end_test_early:
                    print('No more questions available.')
                    utils.save_screenshot(driver,'exception_screenshots',"ques_over")
                    break
            except Exception as e:
                print(e)
                utils.save_screenshot("random_error")
            
        except Exception as e:
            print('Break due to other reason')
            utils.save_screenshot(driver,'exception_screenshots',"break_other")

            topic_ids = get_topic_ids(qdata,chp_id)

            _ , topic_df = qdata.get()
            subject = topic_df[topic_df['Topic ID']==topic_ids[0]].Subject.values[0]
            
            driver.get(custom_exam_url)
            select_sub_tab_and_expand_chp(driver,subject,chp_id)
            break
            


    

    # submit the test 
    sub_test_elm = driver.find_elements(By.XPATH, sub_test_xp)[0]
    driver.execute_script("arguments[0].click();", sub_test_elm)

    return record_df
