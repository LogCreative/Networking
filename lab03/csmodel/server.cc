#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>

pthread_mutex_t mutex;
 
void *serve(void* param)
{
	int this_server = rand();

    time_t clock;
	char dataSending[1025]; // Actually this is called packet in Network Communication, which contain data and send through.
	int clintListn = 0, clintConnt = 0;
	struct sockaddr_in ipOfServer;
	clintListn = socket(AF_INET, SOCK_STREAM, 0); // creating socket
	memset(&ipOfServer, '0', sizeof(ipOfServer));
	memset(dataSending, '0', sizeof(dataSending));
	ipOfServer.sin_family = AF_INET;
	ipOfServer.sin_addr.s_addr = htonl(INADDR_ANY);
	ipOfServer.sin_port = htons(2680); 		// this is the port number of running server
	bind(clintListn, (struct sockaddr*)&ipOfServer , sizeof(ipOfServer));
	listen(clintListn , 1);
 
	while(1)
	{
		pthread_mutex_lock(&mutex);
		printf("\n\nHi,I am running server.Some Client hit me\nServed by Number %d\n", this_server); // whenever a request from client came. It will be processed here.
		clintConnt = accept(clintListn, (struct sockaddr*)NULL, NULL);
 
		clock = time(NULL);
		snprintf(dataSending, sizeof(dataSending), "%.24s\r\n", ctime(&clock)); // Printing successful message
		write(clintConnt, dataSending, strlen(dataSending));
		// Assume that it takes 10 seconds of time.
		// sleep(10);

        close(clintConnt);
		pthread_mutex_unlock(&mutex);
        sleep(1);
    }
 
    return NULL;
}

int main(){

    pthread_mutex_init(&mutex,NULL);

    int p_count = 5;

    pthread_t* pbee = (pthread_t *) malloc(p_count*(sizeof(pthread_t)));
    for(int i = 0; i < p_count; ++i)
        pthread_create(&pbee[i], NULL, serve, NULL);

	for(int i = 0; i < p_count; ++i)
        pthread_join(pbee[i],NULL);

    return 0;
}