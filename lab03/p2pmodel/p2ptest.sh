# !/bin/bash

rm -rf file*
rm -rf result_py.dat
dd if=/dev/zero of=file.txt bs=1024 count=10240
for hostnumber in 2 3 4 5 6 7 8 9 10 11 12 13 14
do
    python centralized.py $hostnumber
done
exit
