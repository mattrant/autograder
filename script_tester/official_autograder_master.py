import json
from copy import deepcopy
from subprocess import call,Popen,PIPE,check_output,CalledProcessError
from sys import stdout,exit
class autograder_outline:
    #file containing the anwser key
    grading_key = None
    student_response = None

    def __init__(self):
        #encode as json to ensure dissambiguation of return value (ie 6 vs "6")
        correct_output = open("grading_key.txt","r")
        file_contents = correct_output.read()
        print file_contents
        self.grading_key = json.loads(file_contents)
        self.student_response = deepcopy(self.grading_key)
        self.clear_student_info()
        self.grade()

    def clear_student_info(self):
        """
        Goes into the student_response dictionary and clears grades and also
        replaces 'expected output' key with 'your output'
        """
        #goes into the student response dict and clears grades, and replaces
        #'expected output' key with 'your output'
        for problem in self.student_response:
            for test_case in self.student_response[problem]:
                del self.student_response[problem][test_case]["expected output"]
                scores = len(self.grading_key[problem][test_case]["input"])
                self.student_response[problem][test_case]["score"] = [0 for score in range(scores)]

    def grade(self):
        """
        Initiates the grading process for every file present in the grading_key
        dictionary
        """
        for problem in self.grading_key:

            file_output_name= problem.split(".")[0]

            if not self.can_compile(problem) :
                # for test_case in self.grading_key[problem]:
                #     for score in self.grading_key[problem][test_case]["score"]:
                #         self.student_response[problem][test_case]["score"].append(0)
                continue

            for test_case in self.grading_key[problem]:
                i = 0
                for program_input in self.grading_key[problem][test_case]["input"]:

                #     p = Popen('./'+file_output_name, stdin = PIPE, stdout = PIPE)
                #     p.wait()
                #     result = p.stdout.read()
                # if result == self.grading_key[problem][test_case]["expected"][i]:
                #     self.student_response[problem][test_case]["score"][i]= 20
                # else:
                #     self.student_response[problem][test_case]["score"][i] = 0
                    pass

        self.report_grade()

    def report_grade(self):
        """
        Creates JSON output for autograder from scores in student_response
        """
        self.print_dictionary(self.student_response)
        self.print_dictionary(self.grading_key)

    def print_dictionary(self,dictionary):
        """
        Prints out the homework related dictionaries in a nice human readable
        format
        Input:
            dictionary: the dictionary to be printed
        """
        print "*"*40
        for problem in dictionary:
            print problem,":"
            for test_case in dictionary[problem]:
                print test_case,":"
                for entry in dictionary[problem][test_case]:
                    print "\t",entry,":",dictionary[problem][test_case][entry]
        print "*"*40

    def can_compile(self,file_name):
        """
        Attempts to compile the specified file. If the compiliation fails all of
        the grades for this file are set to zero.
        Input:
            file_name: the name of the file to be compiled
        """
        file_output_name= file_name.split(".")[0]
        cmd_string = "gcc "+file_name+" -o "+file_output_name
        try:
            check_output(cmd_string.split(" "),)
            return True
        except CalledProcessError as e:
            print "Exiting grading for",file_name,"..."
            return False
        except OSError as e:
            print "Exiting grading for",file_name,"..."
            return False

a = autograder_outline()
