import json
from copy import deepcopy
from subprocess import call,Popen,PIPE,check_output,CalledProcessError,STDOUT,TimeoutExpired
from sys import argv
class autograder_outline:
    grading_key = None
    student_response = None
    failed_compilation = {}
    graded = False
    building_key = False
    skipped_keys = {"max time","compile_string"}

    def __init__(self):
        correct_output = open("grading_key.txt","r")
        file_contents = correct_output.read()
        #parse in json info from grading key
        self.grading_key = json.loads(file_contents)
        if(len(argv)>1 and argv[1] == "--build-grading-key"):
            self.building_key = True
            self.clear_answers()
            self.build_grading_key()
        else:
            self.student_response = deepcopy(self.grading_key)
            self.clear_student_info()
            self.grade()

    def __del__(self):
        if not self.graded and not self.building_key:
            self.report_grade()

    def build_grading_key(self):
        for problem in self.grading_key:

            print("%"*40)
            print("Creating answers for file",problem,"...")
            print("%"*40)
            #extracts the part of the file name before .*
            if not self.can_compile(self.grading_key[problem]["compile_string"],problem):
                continue

            #remove compile_string in order to avoid errors in grading loop


            for test_case in self.grading_key[problem]:
                if test_case in self.skipped_keys:
                    continue;
                i = 0
                for program_input in self.grading_key[problem][test_case]["input"]:
                    max_time = self.grading_key[problem]["max time"]
                    result ,error = self.get_output(problem,program_input,max_time)
                    #get expected answer from JSON file
                    print("~"*40)
                    print("Input:",program_input)
                    print("Accepted Answer:",result)
                    self.grading_key[problem][test_case]["expected output"][i] = result

                    i+=1
        self.write_answers_to_file()
    def write_answers_to_file(self):
        key = open("grading_key.txt","w")
        json_string = self.beautify_json(json.dumps(self.grading_key))
        key.write(json_string)
    def beautify_json(self,json_string):
        """
        Makes the json string human readable
        Input:
            json_string: string to be made human readable
        """

        tabs = 0
        finished_json = ""
        in_array = False

        for c in json_string:
            if c == '{':
                tabs+=1
                finished_json+=c+'\n'+'\t'*tabs
            elif c == '}':
                finished_json+='\n'+'\t'*tabs+c
                tabs-=1
            elif c == ',' and not in_array:
                finished_json+=c+'\n'+'\t'*tabs
            elif c=='[':
                finished_json+=c
                in_array = True
            elif c == ']':
                finished_json+=c
                in_array = False
            else:
                finished_json+=c
        return "".join(finished_json)
    def clear_answers(self):
        for problem in self.grading_key:
            for test_case in self.grading_key[problem]:
                if test_case in self.skipped_keys:
                    continue;
                #sets up a 'blank' array of answers
                self.grading_key[problem][test_case]["expected output"] = [0 for x in self.grading_key[problem][test_case]["input"]]

    def clear_student_info(self):
        """
        Goes into the student_response dictionary and clears grades and also
        replaces 'expected output' key with 'output'
        """
        #goes into the student response dict and clears grades, and replaces
        #'expected output' key with 'your output'
        for problem in self.student_response:
            #student doesn't need compile_string
            del self.student_response[problem]["compile_string"]
            del self.student_response[problem]["max time"]

            for test_case in self.student_response[problem]:

                del self.student_response[problem][test_case]["expected output"]
                #set output key to empty
                self.student_response[problem][test_case]["output"] = []

                scores = len(self.grading_key[problem][test_case]["input"])
                #sets up a score array for with one entry per input
                self.student_response[problem][test_case]["score"] = [0 for score in range(scores)]

    def grade(self):
        """
        Initiates the grading process for every file present in the grading_key
        dictionary
        """
        for problem in self.grading_key:

            print("%"*40)
            print("Grading file",problem,"...")
            print("%"*40)

            #extracts the part of the file name before .*
            file_output_name= problem

            if not self.can_compile(self.grading_key[problem]["compile_string"],problem):
                continue

            #remove compile_string in order to avoid errors in grading loop
            del self.grading_key[problem]["compile_string"]

            max_time = self.grading_key[problem]["max time"]
            del self.grading_key[problem]["max time"]

            for test_case in self.grading_key[problem]:
                i = 0
                for program_input in self.grading_key[problem][test_case]["input"]:

                    result ,error = self.get_output(file_output_name,program_input,max_time)

                    #get expected answer from JSON file
                    expected_output = self.grading_key[problem][test_case]["expected output"][i]
                    if "tolerance"in self.grading_key[problem][test_case]:
                        tolerance = self.grading_key[problem][test_case]["tolerance"]
                        #check if floats are within the tolerance
                        if self.compare_float(result,expected_output,tolerance):
                            self.student_response[problem][test_case]["score"][i]= self.grading_key[problem][test_case]["score"]
                        else:
                            self.print_hint(program_input,result,expected_output,error)
                    else:
                        if result == expected_output:
                            #mark that the student got this one correct
                            self.student_response[problem][test_case]["score"][i]= self.grading_key[problem][test_case]["score"]
                        else:
                            #give hint for problem since it was incorrect
                            self.print_hint(program_input,result,expected_output,error)
                    i+=1
        self.report_grade()
        self.graded = True
    def print_failed_tolerance_check_string(result,expected_output,tolerance):
        result_number = result.split(" ")[-1]
        expected_number = expected_output.split(" ")[-1]
        print("\tResulting number",result_number,"not within tolerance of",tolerance,"from",result_number)

    def compare_float(self,result,expected_output,tolerance):
        """
        Compares results containing floating point numbers to and checks if the
        floating point numbers contained in the results are within the tolerance
        of each other
        Input:
            result: string containing a float as the last value in a string. Must
                    be of the format "<rest of string>  <float>"
            expected_output: string containing a float as the last value in a string.
                             Must conform to the same format as result_array
            tolerance: the tolerance values for the absolute difference of the result
                       float and the expected_output float
        Returns:
            Returns true when the absolute difference of the floats is within
            the tolerance and the string portions of the result and expected_output
            match each other
        """
        #double should always be the last thing in the result seperated by a space
        #with nothing after it
        result_array = result.split(" ")
        expected_array = expected_output.split(" ")
        value = result_array.pop()
        expected_value =  float(expected_array.pop())

        #must ensure last thing in string is a double
        try:
            value = float(value)
        except ValueError:
            return False

        rest_of_result = " ".join(result_array)
        rest_of_expected= " ".join(expected_array)

        #check if expected answer is within percent tolerance of actual answer
        if abs(expected_value-value)<=(tolerance*max(abs(expected_value),abs(value))):
            return rest_of_result==rest_of_expected
        else:
            print(value,"not within",tolerance*100,"percent of",expected_value)
            return False

    def get_output(self,file_name,program_input,max_time):
        """
        Gets output from a program by giving it input to stdin
        Input:
            file_name: name of the prgram to be run
            program_input: input to be sent to the program's stdin
        """
        #start program
        p = Popen('./'+file_name,shell=True,stdin = PIPE, stdout = PIPE,stderr=PIPE)
        #give input to program
        #all python3 strings must be converted to/from bytes with IO
        try:
            result,error =p.communicate(input=bytes(str(program_input),"ascii"),timeout=max_time)
            return (str(result,'ascii'),str(error,'ascii'))
        except TimeoutExpired:
            return ("","Time expired: program took longer than "+str(max_time)+" seconds")

    def report_grade(self):
        """
        Creates JSON output for autograder from scores in student_response
        """
        result = {"scores":{}}
        for problem in self.student_response:
            total_score = 0
            for test_case in self.student_response[problem]:
                #each correct input for a test case is given the full score
                #incorrect responses will have its corresponding index given 0 points
                #if one part of the test case was incorrect the min value will be 0 and
                #no points will be given
                total_score += min(self.student_response[problem][test_case]["score"])
            result["scores"][problem] = total_score
        print(json.dumps(result))

    def print_hint(self,program_input,output,expected_output,error):
        """
        Prints out the hint for the specified arguments
        Input:
            program_input: input provided to graded program
            output: output produced by program for program_input
            expected_output: correct ouput that should result from input of program_input
        """
        print("Incorrect Output")
        print("\tInput:",program_input)
        #repr() will print escape characters
        # (">"*9) used to line up the output and expected output vertically
        #for easier visual comparison of strings
        print("\tOutput"+(">"*9)+":",repr(output))
        if not error=='':
            print("\tError:",repr(error))
        #for unicode encoded strings python will print out u'<contents of string'
        #the purpose of [1:] is to remove the 'u' from the printed output
        print("\tExpected Output:", repr(expected_output))
        print("~"*40)

    def print_dictionary(self,dictionary):
        """
        Prints out the homework related dictionaries in a nice human readable
        format
        Input:
            dictionary: the dictionary to be printed
        """
        print("*"*40)
        for problem in dictionary:
            print(problem,":")
            for test_case in dictionary[problem]:
                print(test_case,":")
                for entry in dictionary[problem][test_case]:
                    print("\t",entry,":",dictionary[problem][test_case][entry])
        print("*"*40)

    def can_compile(self,cmd_string,problem):
        """
        Attempts to compile the specified file. If the compiliation fails, all of
        the grades for this file are set to zero.
        Input:
            cmd_string: string of the compilation command to be executed in the shell
            problem: name of the problem associated with the compile string
        """


        try:
            check_output(cmd_string.split(" "))
            return True
        except CalledProcessError as e:
            print("Compilation error. Exiting grading for problem",problem,"...")
            return False
        except OSError as e:
            print("Compilation error. Exiting grading for problem",problem,"...")
            return False
#perform this action if this file is run as a script
if __name__ == "__main__":
    a = autograder_outline()
