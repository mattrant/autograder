import json
import subprocess
from grading_key_validator import legal_grading_key
import os
correct_returns = {"inf_loop":'{"scores":{"inf_loop":0}}',
"fault":'{"scores":{"fault":0}}',
"missing_file":'{"scores":{"missing_file":0}}',
"correct_double":'{"scores":{"correct_double":1}}',
"incorrect_double":'{"scores":{"incorrect_double":0}}',
"correct_regular":'{"scores":{"correct_regular":1}}',
"incorrect_regular":'{"scores":{"incorrect_regular":0}}',
"incorrect_file":'{"scores":{"incorrect_file":0}}',
"correct_file":'{"scores":{"correct_file":1}}',
"correct_multiple_input": '{"scores":{"correct_multiple_input":1}}',
"incorrect_multiple_input": '{"scores":{"incorrect_multiple_input":0}}',
"correct_multiple_cases":'{"scores":{"correct_multiple_cases":2}}',
"incorrect_multiple_cases":'{"scores":{"incorrect_multiple_cases":0}}',
"correct_single_input":'{"scores":{"correct_single_input":1}}',
"illegal_utf":'{"scores":{"illegal_utf":0}}'
}

test_case = json.loads(open("grading_key.json","r").read())
all_correct =0

check = u'\u2713'
x_mark = u'\u2717'
green_color = '\033[92m'
end_color = '\033[0m'
red_color = '\033[91m'
for t in test_case:
    try:
        print("Test Case:",t,"... ",end="",flush=True)
        temp_dict = {t:test_case[t]}
        open("grading_key.txt","w").write(json.dumps(temp_dict))
        results = str(subprocess.check_output(['python3','autograder.py'],timeout=10),'utf-8',errors='ignore')
        #TODO: check for JSON string at end of output more robustly
        #json string could have a number of newlines after it
        json_return_str =results.split("\n")[-2]
        actual_dict = json.loads(json_return_str)
        expected_dict = json.loads(correct_returns[t])

        if actual_dict!=expected_dict or expected_dict!=actual_dict:
            print(red_color+x_mark+end_color)
            print("\tExpected:",expected_dict)
            print("\tActual>>:",actual_dict)
        else:
            print(green_color+check+end_color)
            all_correct+=1;
    except ValueError as v:
        print(red_color+x_mark+end_color)
        print(v)
        print(repr(json_return_str))
    except subprocess.TimeoutExpired as e:
        print(red_color+x_mark+end_color)
        print("\tFailed to stop process within time limit")
    except subprocess.CalledProcessError as e:
        print(red_color+x_mark+end_color)
        print("autograder exited abnormally with return code",e.returncode)
        print("Error output:",e.output)

#cleanup object files
for k in correct_returns:
    if os.path.isfile(k):
        os.remove(k)

os.remove("grading_key.txt")
