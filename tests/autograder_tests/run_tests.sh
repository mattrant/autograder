#!/bin/bash
files=("autograder.py" "grading_key_validator.py")
for i in ${files[@]}
do
        cp ../../${i} .
done
python3 autograder_test_script.py
for i in ${files[@]}
do
        rm ${i}
done
