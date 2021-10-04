#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>
#include <time.h> //contains various functions for manipulating date and time

#define MAXLINE 102400

int main(int argc, char* argv[])
{
    int CreateSocket = 0,n = 0;
    char dataReceived[MAXLINE];
    struct sockaddr_in ipOfServer;
 
    memset(dataReceived, 1 ,sizeof(dataReceived));
 
    if((CreateSocket = socket(AF_INET, SOCK_STREAM, 0))< 0)
    {
        printf("Socket not created \n");
        return 1;
    }
 
    ipOfServer.sin_family = AF_INET;
    ipOfServer.sin_port = htons(2680);
    if(argc==1){
        fprintf(stderr,"No server ip assigned. Use 127.0.0.1 as default.\n");
        ipOfServer.sin_addr.s_addr = inet_addr("127.0.0.1");
    } else {
        ipOfServer.sin_addr.s_addr = inet_addr(argv[1]);
    }
 
    if(connect(CreateSocket, (struct sockaddr *)&ipOfServer, sizeof(ipOfServer))<0)
    {
        printf("Connection failed due to port and ip problems\n");
        return 1;
    }

    for(int i = 0; i < MAXLINE/1024; ++i)
        read(CreateSocket, dataReceived + (i*1024) , 1024);
    
    char filename[80];
    if (argc == 3)
        sprintf(filename, "file_receive_%s.txt",argv[2]);   
    else
        sprintf(filename, "file_receive.txt");

    FILE* f = fopen(filename,"wb");
    fwrite(dataReceived,sizeof(char),MAXLINE,f);
    fclose(f);

    if( n < 0)
    {
        printf("Standard input error \n");
    }
 
    return 0;
}
