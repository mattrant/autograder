from os import listdir, remove
import subprocess
import grading_key_validator
"""
All test cases should follow the format grading_key.txt-<identifier>. There should
be no hyphens present in the identifier. Thisscript will run through all test keys
present in the directory and make subprocess that the validator returns the correct
result for each test case. Each file will be have its contents coppied to a file
named grading_key.txt and the validator will be run for each case.
"""
correct_results = {
    'missing_max_time':False,
    'missing_problem':False,
    'wrong_type_output':False,
    'missing_input':False,
    'wrong_type_tolerance':False,
    'wrong_type_input':False,
    'wrong_type_run_string':False,
    'missing_run_string':False,
    'input_longer_than_output':False,
    'legal_multiple_cases':True,
    'missing_test_case':False,
    'missing_score':False,
    'missing_expected_output':False,
    'legal_multiple_problems':True,
    'missing_compile_string':False,
    'legal_single_problem':True,
    'dup_key':False,
    'illegal_json':False
}
check = u'\u2713'
x_mark = u'\u2717'
green_color = '\033[92m'
end_color = '\033[0m'
red_color = '\033[91m'

test_cases = []
for entry in listdir():
    if ".txt" in entry:
        test_cases.append(entry)
grading_key_validator.suppress_output= True
for t in test_cases:
    try:
        name = t.split("-")[1]
        print("Test Case:",name,"... ",end="",flush=True)
        f= open("grading_key.txt","w")
        f.truncate()
        f.write(open(t).read())
        f.close()

        #TODO: check for JSON string at end of output more robustly
        #json string could have a number of newlines after it
        results = grading_key_validator.legal_grading_key()
        if results != correct_results[name]:
            print(red_color+x_mark+end_color)
            print("\tExpected:",correct_results[name])
            print("\tActual>>:",results)
        else:
            print(green_color+check+end_color)
    except subprocess.TimeoutExpired as e:
        print(red_color+x_mark+end_color)
        print("\tFailed to stop process within time limit")
    except subprocess.CalledProcessError as e:
        print(red_color+x_mark+end_color)
        print("\tautograder exited abnormally with return code",e.returncode)
        print("\tError output:",e.output)

remove("grading_key.txt")
