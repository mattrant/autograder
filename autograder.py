import json
from copy import deepcopy
from subprocess import call,Popen,PIPE,check_output,CalledProcessError,STDOUT,TimeoutExpired
from sys import argv,exit,stdout
import os.path
from grading_key_validator import legal_grading_key


class autograder_outline:
    grading_key = None
    student_response = None
    failed_compilation = {}
    reported = False
    building_key = False
    skipped_keys = {"max time","compile_string"}
    cmdline_flags = {"--build-grading-key":None,"--validate-key":None}

    def __init__(self):
        correct_output = open("grading_key.txt","r")
        file_contents = correct_output.read()
        #parse in json info from grading key
        self.register_flag_table()
        try:
            self.grading_key = json.loads(file_contents)
        except ValueError as v:
            print("Illegal JSON formatting. Please ensure that the grading key is legal JSON")
            print("\t>>Error:",v)
            exit(0)

        if len(argv)>1:
            try:
                for flag in argv[1:]:
                    self.cmdline_flags[flag]()
            except KeyError as k:
                print(k,"is not a legal flag")
                exit(0)
        else:
            self.student_response = deepcopy(self.grading_key)
            self.clear_student_info()
            self.grade()

    def register_flag_table(self):
        """
        Registers the functions to a jump table that is used to map command line
        arguments to their repective functions
        """
        self.cmdline_flags["--build-grading-key"] = self.build_grading_key
        self.cmdline_flags["--validate-key"] = self.validate_key

    def validate_key(self):
        """
        Ensures that the file grading_key.txt (if it exists) conforms to the
        specification of a proper grading key.
        """
        #TODO:fix this odd key setting being used to prevent __del__ from running
        self.building_key = True
        if legal_grading_key():
            print("Valid grading_key.txt");
        else:
            print("Invalid grading_key.txt")

    def __del__(self):
        if not self.building_key and not self.reported:
            self.report_grade()
    def build_grading_key(self):
        """
        Builds a grading key from the responses obtained from the programs specified
        in the file grading_key.txt
        """
        self.building_key = True
        self.clear_answers()
        for problem in self.grading_key:

            print("%"*40)
            print("Creating answers for file",problem,"...")
            print("%"*40)
            #extracts the part of the file name before .*
            if not self.can_compile(self.grading_key[problem]["compile_string"],problem):
                continue

            for test_case in self.grading_key[problem]:
                if test_case in self.skipped_keys:
                    continue;
                i = 0
                for program_input in self.grading_key[problem][test_case]["input"]:
                    max_time = self.grading_key[problem]["max time"]
                    run_string = self.grading_key[problem][test_case]["run string"][i]
                    result ,error = self.get_output(run_string,program_input,max_time)
                    #get expected answer from JSON file
                    print("~"*40)
                    print("Input:",program_input)
                    print("Accepted Answer:",result)
                    self.grading_key[problem][test_case]["expected output"][i] = result

                    i+=1
        self.write_answers_to_file()
    def write_answers_to_file(self):
        """
        Writes grading_key to a file named grading_key.txt after the JSON
        has been made human readable
        """
        key = open("grading_key.txt","w")
        json_string = beautify_json(json.dumps(self.grading_key))
        key.write(json_string)

    def clear_answers(self):
        """
        Clears the answers present in the grading key and sets the expected_output
        array to an array of the same length as the correspoinding input array
        initialized with all zeros
        """
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
                    #mainly needed for clear output for incorrect file contents

                    hint_dict = {}

                    program_input = str(program_input)
                    run_string = self.grading_key[problem][test_case]["run string"][i]

                    result ,error = self.get_output(run_string,program_input,max_time)

                    #get expected answer from JSON file
                    expected_output = str(self.grading_key[problem][test_case]["expected output"][i])


                    #check if file contents should be compared
                    #TODO:put this in a separate function
                    if("check files" in self.grading_key[problem][test_case]):

                        #prevent whitespace after the filename to prevent empty filename when parsing
                        expected_output=expected_output.strip()
                        #removes the last '-' seperated portion of the file name
                        #remove the last space separated word from the expected_output string
                        correct_stdout =" ".join(expected_output.split(" ")[:-1])
                        answer_file_name = expected_output.split(" ")[-1]

                        (student_contents,answer_contents) = self.get_file_contents(answer_file_name);

                        if(student_contents == answer_contents and result == correct_stdout):
                            self.student_response[problem][test_case]["score"][i]= self.grading_key[problem][test_case]["score"]
                        else:
                            if(student_contents!=answer_contents):
                                student_file_name = self.get_student_file_name(answer_file_name)
                                hint_dict[student_file_name] = (student_contents,answer_contents)
                            if(result != correct_stdout):
                                hint_dict["Output"] = (result,correct_stdout)

                    elif "tolerance"in self.grading_key[problem][test_case]:
                        tolerance = self.grading_key[problem][test_case]["tolerance"]
                        #check if floats are within the tolerance
                        if self.compare_float(result,expected_output,tolerance):
                            self.student_response[problem][test_case]["score"][i]= self.grading_key[problem][test_case]["score"]
                        else:
                            hint_dict["Output"] = (result,expected_output)
                    else:
                        if result == expected_output:
                            #mark that the student got this one correct
                            self.student_response[problem][test_case]["score"][i]= self.grading_key[problem][test_case]["score"]
                        else:
                            #give hint for problem since it was incorrect
                            hint_dict["Output"] = (result,expected_output);

                    self.print_hint(program_input,hint_dict,error);
                    i+=1
        self.report_grade()
        self.reported = True
    def get_student_file_name(self,answer_file_name):
        """
        Parses the name of the student file out of the name of the answer file
        provided in expected_output
        Input:
            answer_file_name
        Returns:
            A string containing the student file name
        """
        return "".join(answer_file_name.split("-")[:-1])
    def get_file_contents(self,answer_file_name):
        """
        Gets the content from both the student file and the answer file
        Input:
            asnwer_file_name: the name of the answer file that has the student filename
                        embedded within it
        Returns:
            The contents of both the student file and the answer file in a tuple
            with the format: (student_contents,answer_contents)
        """
        student_file_name = self.get_student_file_name(answer_file_name);

        student_contents = ""

        if not os.path.isfile(answer_file_name):
            print("Answer file not found:",answer_file_name)
            #answer files should be present
            #someone must have forgot to upload them
            raise OSError("File not Found:",answer_file_name)

        answer_contents = open(answer_file_name,"rt").read()

        if not os.path.isfile(student_file_name):
            print("File not found:",student_file_name)
        else:
            student_contents = open(student_file_name,"rt").read()

        return (student_contents,answer_contents)

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

    def get_output(self,run_string,program_input,max_time):
        """
        Gets output from a program by giving it input to stdin
        Input:
            run_string: command to be passed to the shell to run the program to be graded
            program_input: input to be sent to the program's stdin
            max_time: maximum allowed time for a program to produce an output
        Returns:
            Returns the tuple (output,error) where output is the output of the
            program and error is the error output of the program
        """
        #start program
        #TODO:catch error if run_string fails
        p = Popen(run_string,shell=True,stdin = PIPE, stdout = PIPE,stderr=PIPE)
        print(run_string);

        try:
            result,error =p.communicate(input=bytes(str(program_input),"ascii"),timeout=max_time)
            return (str(result,'utf-8',errors="ignore"),str(error,'utf-8',errors="ignore"))
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

    def print_hint(self,program_input,hint_dict,error):
        """
        Prints out the hint for the specified arguments
        Input:
            program_input: input provided to graded program
            hint_dict: The keys of the entries should be the strings that should
                        be printed to output to identify where the output originated.
                        The values of the dict should be tuples in the form
                        (output,expected_output).
            error: the error output of the program
        """
        if len(hint_dict) != 0:
            print("Incorrect Output")
            print("\tInput:",repr(string_to_stdout_encoding(program_input)))
        if not error=='':
            print("\tError:",repr(string_to_stdout_encoding(error)))


        for k in hint_dict:
            (output,expected_output) = hint_dict[k]
            #repr() will print escape characters
            # (">"*9) used to line up the output and expected output vertically
            #for easier visual comparison of strings
            print("\t"+k+(">"*9)+":",repr(string_to_stdout_encoding(output)))

            #for unicode encoded strings python will print out u'<contents of string'
            #the purpose of [1:] is to remove the 'u' from the printed output
            print("\tExpected "+k+":", repr(string_to_stdout_encoding(expected_output)))
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
        Returns:
            True when the compilation succeeded with no errors
        """


        try:
            print(cmd_string)
            check_output(cmd_string.split(" "),stderr=STDOUT)
            return True
        except CalledProcessError as e:
            # end='' is used to suppress the newline from print() in python 3.x
            #TODO: see if it's possible to make backslashreplace the default handler
            print(e.output.decode(stdout.encoding,"backslashreplace"),end='')
            print("Compilation error. Exiting grading for problem",problem,"...")
            return False
        except OSError as e:
            print("Compilation error. Exiting grading for problem",problem,"...")
            return False

def string_to_stdout_encoding(string):
    """
    Takes a string, encodes it to the encoding supported by stdout, and decodes
    the byte representation encoding back to a string in the same format.
    Characters that are illegal in the supported encoding are replaced by the
    backslashreplace UnicodeError handler
    Input:
        string: the string to be changed
    """
    return string.encode(stdout.encoding,"backslashreplace").decode(stdout.encoding)

def beautify_json(json_string):
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


if __name__ == "__main__":
    a = autograder_outline()
