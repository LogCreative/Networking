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

int main(int argc, char* argv[])
{
    struct sockaddr_in ipOfServer;
    ipOfServer.sin_family = AF_INET;
    ipOfServer.sin_port = htons(2680);
    ipOfServer.sin_addr.s_addr = inet_addr("127.0.0.1");
    
    char filename[80];
    sprintf(filename, "file_receive.txt");

    int MAXLINE = 1024;

    switch (argc)
    {
    case 1:
        printf("./client [file_size] [target_ip] [host_number]\n");
        return 0;
    case 4:
        sprintf(filename, "file_receive_%s.txt",argv[3]);
    case 3:
        ipOfServer.sin_addr.s_addr = inet_addr(argv[2]);
    case 2:
        MAXLINE = atoi(argv[1]);
    default:
        break;
    }

    clock_t start,finish;
    start = clock();

    int CreateSocket = 0,n = 0;
    char* dataReceived = (char*)malloc(MAXLINE*sizeof(char));
    memset(dataReceived, 1 ,sizeof(dataReceived));
 
    if((CreateSocket = socket(AF_INET, SOCK_STREAM, 0))< 0)
    {
        printf("Socket not created \n");
        return 1;
    }

    if(connect(CreateSocket, (struct sockaddr *)&ipOfServer, sizeof(ipOfServer))<0)
    {
        printf("Connection failed due to port and ip problems\n");
        return 1;
    }

    for(int i = 0; i < MAXLINE/1024; ++i)
        read(CreateSocket, dataReceived + (i*1024) , 1024);

    FILE* f = fopen(filename,"wb");
    fwrite(dataReceived,sizeof(char),MAXLINE,f);
    fclose(f);

    finish = clock();

    FILE* rf = fopen("result_c.dat","a");
    double speed = MAXLINE/((double)(finish-start)/CLOCKS_PER_SEC)*8; // measured in Mbps
    if (argc==4)
        fprintf(rf,"%s\t%f\n",argv[3],speed);
    else fprintf(rf,"\t%f\n",speed);
    fclose(rf);
    fprintf(stdout, "%f\n", speed);

    if( n < 0)
    {
        printf("Standard input error \n");
    }
 
    return 0;
}
