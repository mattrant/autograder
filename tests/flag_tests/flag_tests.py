
import subprocess
import json
correct_returns ={
'--build-grading-key':'{"scores": {"savestr": 30, "maxarray": 30, "findstr": 40}}',
'--validate-key':True
}

print("Running autograder flag tests...")
#build-key check
subprocess.check_output(['python3','autograder.py','--build-grading-key'],timeout=10)
results = str(subprocess.check_output(['python3','autograder.py'],timeout=10),'utf-8',errors='ignore')
print("Test Case: --build-grading-key... ",end="",flush=True)
#TODO: check for JSON string at end of output more robustly
#json string could have a number of newlines after it
json_return_str =results.split("\n")[-2]
actual_dict = json.loads(json_return_str)
expected_dict = json.loads(correct_returns['--build-grading-key'])

check = u'\u2713'
x_mark = u'\u2717'
green_color = '\033[92m'
end_color = '\033[0m'
red_color = '\033[91m'

if actual_dict!=expected_dict or expected_dict!=actual_dict:
    print(red_color+x_mark+end_color)
    print("\tExpected:",expected_dict)
    print("\tActual>>:",actual_dict)
else:
    print(green_color+check+end_color)
#--validate-key test_case
print("Test Case: --validate-key ... ",end="",flush=True)
results = str(subprocess.check_output(['python3','autograder.py','--validate-key'],timeout=10),'utf-8',errors='ignore')
status = results.split('\n')[-2]
if "Valid" in status:
    print(green_color+check+end_color)
else:
    print(red_color+x_mark+end_color)
    print("\tExpected: Valid grading_key.txt")
    print("\tActual>>:",status)
