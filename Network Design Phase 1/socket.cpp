#include "socket.h"
#include <sys/socket.h>
#include <netinet/in.h>


void createUDPServer ( int port, int *socketDescriptor, sockaddr_in *socketAddress ) {

	*socketDescriptor = socket( AF_INET, SOCK_DGRAM, 0 ) ;
			
	socketAddress->sin_family = AF_INET ;
	socketAddress->sin_addr.s_addr = INADDR_ANY ;
	socketAddress->sin_port = htons(port) ;

	bind( *socketDescriptor, ( struct sockaddr* )socketAddress, sizeof( socketAddress ) < 0) ;
		
}

void createUDPCLient( int *socketDescriptor ) {

	*socketDescriptor = socket( AF_INET, SOCK_DGRAM, 0 ) ;

}
