import json
from copy import deepcopy
from subprocess import call,Popen,PIPE,check_output,CalledProcessError,STDOUT
from sys import argv
class autograder_outline:
    grading_key = None
    student_response = None
    failed_compilation = {}
    graded = False
    building_key = False

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

            print "\nCreating answers for file",problem,"..."

            #extracts the part of the file name before .*
            file_output_name= problem.split(".")[0]

            if not self.can_compile(problem):
                continue

            for test_case in self.grading_key[problem]:
                i = 0
                for program_input in self.grading_key[problem][test_case]["input"]:

                    result ,error = self.get_output(file_output_name,program_input)
                    #get expected answer from JSON file
                    print "~"*40
                    print "Input:",program_input
                    print "Accepted Answer:",result
                    self.grading_key[problem][test_case]["expected output"][i] = result

                    i+=1
        self.write_answers_to_file()
    def write_answers_to_file(self):
        key = open("grading_key.txt","w")
        json_string = self.beautify_json(json.dumps(self.grading_key))
        key.write(json_string)
    def beautify_json(self,json_string):

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

            #extracts the part of the file name before .*
            file_output_name= problem.split(".")[0]

            if not self.can_compile(problem):
                continue

            for test_case in self.grading_key[problem]:
                i = 0
                for program_input in self.grading_key[problem][test_case]["input"]:

                    result ,error = self.get_output(file_output_name,program_input)
                    #get expected answer from JSON file
                    expected_output = self.grading_key[problem][test_case]["expected output"][i]

                    if result == expected_output:
                        #mark that the student got this one correct
                        self.student_response[problem][test_case]["score"][i]= self.grading_key[problem][test_case]["score"]
                    else:
                        #give hint for problem since it was incorrect
                        self.print_hint(program_input,err,expected_output)
                    i+=1
        self.report_grade()
        self.graded = True

    def get_output(self,file_name,program_input):
        #start program
        p = Popen('./'+file_name,shell=True,stdin = PIPE, stdout = PIPE,stderr=PIPE)
        #give input to program
        return p.communicate(input=str(program_input))


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
        #repr() will print escape characters
        print "\tOutput:",repr(output)
        #for unicode encoded strings python will print out u'<contents of string'
        #the purpose of [1:] is to remove the 'u' from the printed output
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
