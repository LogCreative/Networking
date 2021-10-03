# !/bin/bash

g++ server.cc -o server -pthread
g++ client.cc -o client -pthread
./server &
./client
diff file.txt file_send.txt
diff file.txt file_receive.txt
exit
