import json
from copy import deepcopy
from subprocess import call,Popen,PIPE,check_output,CalledProcessError

class autograder_outline:
    #file containing the anwser key
    grading_key = None
    student_response = None
    failed_compilation = {}
    graded = False

    def __init__(self):
        #encode as json to ensure dissambiguation of return value (ie 6 vs "6")
        correct_output = open("grading_key.txt","r")
        file_contents = correct_output.read()
        #parse in json info from grading key
        self.grading_key = json.loads(file_contents)
        self.student_response = deepcopy(self.grading_key)
        self.clear_student_info()
        self.grade()

    def __del__(self):
        if not self.graded:
            self.report_grade()

    def clear_student_info(self):
        """
        Goes into the student_response dictionary and clears grades and also
        replaces 'expected output' key with 'output'
        """
        #goes into the student response dict and clears grades, and replaces
        #'expected output' key with 'your output'
        for problem in self.student_response:
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

            print "\nGrading file",problem,"..."

            file_output_name= problem.split(".")[0]

            if not self.can_compile(problem):
                continue

            for test_case in self.grading_key[problem]:
                i = 0
                for program_input in self.grading_key[problem][test_case]["input"]:
                    #start program
                    p = Popen('./'+file_output_name, stdin = PIPE, stdout = PIPE)
                    #give input to program
                    p.stdin.write(str(program_input))
                    p.stdin.flush()
                    #wait for program to produce answer
                    p.wait()
                    result = p.stdout.read()

                    expected_output = self.grading_key[problem][test_case]["expected output"][i]

                    if result == expected_output:
                        #mark that the student got this one correct
                        self.student_response[problem][test_case]["score"][i]= self.grading_key[problem][test_case]["score"]
                    else:
                        #give hint for problem since it was incorrect
                        self.print_hint(program_input,result,expected_output)
                    i+=1
        self.report_grade()
        self.graded = True

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
        print json.dumps(result)

    def print_hint(self,program_input,output,expected_output):
        """
        Prints out the hint for the specified arguments
        """
        print "Incorrect Output"
        print "\tInput:",program_input
        print "\tOutput:",repr(output)
        print "\tExpected Output:", repr(expected_output)[1:]

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
        Attempts to compile the specified file. If the compiliation fails, all of
        the grades for this file are set to zero.
        Input:
            file_name: the name of the file to be compiled
        """
        #takes file name and removes .c from it
        file_output_name= file_name.split(".")[0]
        #builds the command to compile the file
        cmd_string = "gcc "+file_name+" -o "+file_output_name

        try:
            check_output(cmd_string.split(" "))
            return True
        except CalledProcessError as e:
            print "Compilation error. Exiting grading for",file_name,"..."
            return False
        except OSError as e:
            print "Compilation error. Exiting grading for",file_name,"..."
            return False
#perform this action if this file is run as a script
if __name__ == "__main__":
    a = autograder_outline()
