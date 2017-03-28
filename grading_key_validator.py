import json
import os
import sys
def dup_check(pairs):
    """
    Checks for duplicate values present in the grading key. If a duplicate key is
    found the name and value of the second instance is printed to the screen.
    Input:
        pairs: a list of pairs of values that should be placed into a dictionary
    Returns:
        A dictionary of the pairs after they have been checked for duplicates
    """
    d = {}
    for k,v in pairs:
        if k in d:
            print("Error: more than one instance of key",repr(k),"at same depth")
            print("\tFirst instance of key",repr(k),"has value",d[k])
            print("\tSecond instance of key",repr(k),"has value",v)
            sys.exit(0)
        else:
            d[k] = v
    return d

def legal_grading_key():
    """
    Checks whether grading_key.txt follows the formatting rules for the autograder.
    Returns:
        True if the key conforms to the format for grading keys
    """
    if not os.path.isfile("grading_key.txt"):
        print("Grading key not found or file is not named grading_key.txt")
        return False;

    key = open("grading_key.txt","r")
    contents = "";
    try:
        contents = json.loads(key.read(),object_pairs_hook=dup_check)
    except ValueError as v:
        print("Illegal JSON formatting. Please ensure that the grading key is legal JSON")
        print("\t>>Error:",v)
        return False

    return check_key_structure(contents)

def check_key_structure(key):
    """
    Checks the entries in the entire grading_key.txt file to ensure that the
    proper keys are found. There must be no duplicate keys or keys with illegal
    value types. There must also be at least one test case per problem and input
    and output array lengths must match
    Returns:
        True if the grading key dictionary comforms to the expected format
    """
    is_legal_key = True;
    problems = {}
    for k in key:
        if type(key[k]) != dict:
            print("Illegal key at top level of grading key. Key must be a HW Problem (JSON Dictionary)");
        else:
            problems[k] = key[k]

    print(40 * '~')

    for p in problems:
        print("Validating problem",repr(p),"...")

        required_problem_keys = {"max time":int,"compile_string":str}
        test_case_present = False

        test_cases ={}
        for k in problems[p]:
            if k in required_problem_keys:
                if type(problems[p][k]) == required_problem_keys[k]:
                    del required_problem_keys[k]
                else:
                    print("Error: key",repr(k),"has value of type",
                    type(problems[p][k]).__name__,". Value must be of type",required_problem_keys[k].__name__)
                    is_legal_key = False;
            elif type(problems[p][k]) == dict:
                #must be a test case
                test_cases[k] = problems[p][k]
                test_case_present = True
            else:
                print("Illegal key",repr(k))
                is_legal_key = False

        if not test_case_present:
            print("Error: must contain at least 1 test case")
            is_legal_key = False

        for k in required_problem_keys:
            print("Error: Problem",repr(p)," must contain the key",repr(k),"with a value of type",required_problem_keys[k].__name__)
            is_legal_key = False
        for t in test_cases:

            required_test_case_keys = {"expected output":list,"input":list,"score":int,"run string":list}
            optional_test_case_keys = {"check files":bool,"tolerance":float}
            length_match =  {"expected output":list,"input":list,"run string":list}

            for k in test_cases[t]:
                if k in required_test_case_keys:
                    if type(test_cases[t][k]) == required_test_case_keys[k]:
                        del required_test_case_keys[k]
                    else:
                        print("Error: Test Case",t,": key",repr(k),"must contain a value of type",required_test_case_keys[k].__name__)
                        is_legal_key = False
                elif k in optional_test_case_keys:
                    if type(test_cases[t][k]) == optional_test_case_keys[k]:
                        del optional_test_case_keys[k]
                    else:
                        print("Error: Test Case",t,": key",repr(k),"must contain a value of type",optional_test_case_keys[k].__name__)
                        is_legal_key = False
                else:
                    print("Error: Test Case",t,": illegal key",repr(k),"present")
                    is_legal_key = False
            if not ( "expected output" in required_test_case_keys or "input" in required_test_case_keys or "run string"):
                if len(test_cases[t]["expected output"]) != len(test_cases[t]["input"] and len(test_cases[t]["input"] !=len(test_cases[t]["run string"]))):
                    print("Error: Test case",repr(t),": 'expected output' and 'input' must be of equal length")
                    is_legal_key = False
            for key in required_test_case_keys:
                print("Error: Test case",repr(t),"must contain the key",repr(key),"with a value of type",required_test_case_keys[key].__name__)
                is_legal_key = False
        print (40 *'~')
    return is_legal_key
if __name__ == "__main__":
    if legal_grading_key():
        print("Valid grading_key.txt");
    else:
        print("Invalid grading_key.txt")
