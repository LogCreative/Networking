#include <stdio.h> // standard input and output library
#include <stdlib.h> // this includes functions regarding memory allocation
#include <string.h> // contains string functions
#include <errno.h> //It defines macros for reporting and retrieving error conditions through error codes
#include <unistd.h> //contains various constants
#include <sys/types.h> //contains a number of basic derived types that should be used whenever appropriate
#include <arpa/inet.h> // defines in_addr structure
#include <sys/socket.h> // for socket creation
#include <netinet/in.h> //contains constants and structures needed for internet domain addresses
#include <pthread.h>

char* dataSending; // Actually this is called packet in Network Communication, which contain data and send through.
int fsize;

void* send_thread(void* conn_void_ptr){
	int clintConnt = *((int*)conn_void_ptr);
	pthread_detach(pthread_self());
	free(conn_void_ptr);
	write(clintConnt, dataSending, sizeof(char)*fsize);
	close(clintConnt);
}

int main()
{
	int clintListn = 0;
	struct sockaddr_in ipOfServer;
	clintListn = socket(AF_INET, SOCK_STREAM, 0); // creating socket
	memset(&ipOfServer, '0', sizeof(ipOfServer));
	ipOfServer.sin_family = AF_INET;
	ipOfServer.sin_addr.s_addr = htonl(INADDR_ANY);
	ipOfServer.sin_port = htons(2680); 		// this is the port number of running server
	bind(clintListn, (struct sockaddr*)&ipOfServer , sizeof(ipOfServer));
	listen(clintListn , 20);
 
	int* clintConnt;
	pthread_t th;

	FILE* f;
	if((f = fopen("file.txt","rb"))==NULL){
		fprintf(stderr, "Can't open file file.txt.\n");
		return -1;
	}
	fseek(f,0,SEEK_END);
	fsize = ftell(f);
	fseek(f,0,SEEK_SET);
	dataSending = (char*)malloc(sizeof(char)*fsize);
	printf("%d\n",fsize);
	fread(dataSending, sizeof(char), fsize, f);
	fclose(f);

	f = fopen("file_send.txt","wb");
    fwrite(dataSending,sizeof(char),fsize,f);
    fclose(f);

	f = fopen("result_c.dat","w");
	fprintf(f,"Host\tSpeed\n");
	fclose(f);

	while(1)
	{
		printf("\n\nHi,I am running server.Some Client hit me\n"); // whenever a request from client came. It will be processed here.
		
		clintConnt = (int*)malloc(sizeof(int));
		*clintConnt = accept(clintListn, (struct sockaddr*)NULL, NULL);

		pthread_create(&th, NULL, send_thread, clintConnt);
    }
 
    return 0;
}
