import json
from copy import deepcopy
from subprocess import call,Popen,PIPE

class autograder_outline:
    #file containing the anwser key
    grading_key = None
    student_response = None

    def __init__(self):
        #encode as json to ensure dissambiguation of return value (ie 6 vs "6")
        correct_output = open("grading_key.txt","r")
        self.grading_key = json.loads(correct_output.read())
        self.student_response = deepcopy(self.grading_key)
        self.clear_student_grades()
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
                self.student_response[problem][test_case]["score"] = []
                del self.student_response[problem][test_case]["expected output"]
                self.student_response[problem][test_case]["your output"] = []

    def grade(self):
        """
        Initiates the grading process for every file present in the grading_key
        dictionary
        """
        for problem in a.grading_key:
            print problem,":"
            file_output_name= problem.split(".")[0]

            if not can_compile(problem) :
                continue

            for test_case in a.grading_key[problem]:
                print test_case,":"
                for entry in a.grading_key[problem][test_case]:
                    print "\t",entry,":",a.grading_key[problem][test_case][entry]

    def can_compile(self,file_name):
        """
        Attempts to compile the specified file. If the compiliation fails all of
        the grades for this file are set to zero.
        Input:
            file_name: the name of the file to be compiled
        """
        file_output_name= file_name.split(".")[0]
        try:
            call(['gcc', file_name, '-o', file_output_name])
            return True
        #TODO: replace this error with the error that will get thrown
        except Error as e:
            print "Error has occurred"
            return False
            #TODO:set all grades for this problem to 0 if it failes

a = autograder_outline()
print "~"*40

for problem in a.grading_key:
    print problem,":"
    for test_case in a.grading_key[problem]:
        print test_case,":"
        for entry in a.grading_key[problem][test_case]:
            print "\t",entry,":",a.grading_key[problem][test_case][entry]
        #if type of test_case is list ....
    print "*"*40
