from Student import Student
from QData import QData

import utils
import sys,time


driver = utils.get_driver()
question_data = QData()
login_cred = '9560795635' # phone number or email
student = Student(driver,sys.argv[1])

student.login()

# # wait for otp
# # later on this will be changed to constant OTP
input("enter OTP and press return to continue")
time.sleep(2)

student.take_adp_test(driver,question_data,0.9)


# student.take_full_adp_test(driver,"Physics",question_data)

# student.take_mock_test(driver,question_data)

