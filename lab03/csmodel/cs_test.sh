# !/bin/bash

rm -rf file*
dd if=/dev/zero of=file.txt bs=1024 count=100
g++ server.cc -o server -pthread
g++ client.cc -o client
./server &
./client
diff file.txt file_send.txt
diff file.txt file_receive.txt
exit
