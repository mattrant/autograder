cd tests
for f in *; do
    if [[ -d $f ]]; then
        cd $f
	      ./run_tests.sh $1
        cd ..
    fi
done
