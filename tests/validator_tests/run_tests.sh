#!/bin/bash
files=("autograder.py" "grading_key_validator.py")
for i in ${files[@]}
do
        cp ../../${i} .
done
python3 validator_test_script.py $1
for i in ${files[@]}
do
        rm ${i}
done
