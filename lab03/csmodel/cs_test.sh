# !/bin/bash

rm -rf file*
dd if=/dev/zero of=file.txt bs=1024 count=100
g++ server.cc -o server -pthread
g++ client.cc -o client
./server &
./client
xxd file.txt > file.hex
xxd file_receive.txt > file_receive.hex
# diff file.txt file_send.txt
diff file.hex file_receive.hex
exit
