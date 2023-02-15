#ifndef SOCKET_H
#define SOCKET_H

#include <sys/socket.h>
#include <netinet/in.h>

void createUDPServer( int port, int *socketDescriptor, sockaddr_in *socketAddress ) ;
void createUDPClient( int *socketDescriptor ) ;

#endif
