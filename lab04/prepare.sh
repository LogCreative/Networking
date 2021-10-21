# !/bin/bash

rm -rf file*
rm -rf result_c.dat
dd if=/dev/zero of=file.txt bs=1024 count=10240
g++ server.cc -o server -pthread
g++ client.cc -o client