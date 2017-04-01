files=("autograder.py" "grading_key_validator.py")

for i in ${files[@]}
do
        cp ../../${i} .
done

python3 flag_tests.py

for i in ${files[@]}
do
        rm ${i}
done
