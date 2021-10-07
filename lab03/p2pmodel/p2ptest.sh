# !/bin/bash

rm -rf file*
rm -rf result_py.dat
dd if=/dev/zero of=file.txt bs=1024 count=10240
python centralized.py
# python server.py &
# sleep 1
# python client.py 10485760
# xxd file.txt > file.hex
# xxd file_receive.txt > file_receive.hex
# # diff file.txt file_send.txt
# diff file.hex file_receive.hex
exit
