#include "socket.h"
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <iostream>
#include <unistd.h>



int main ( int argc, char *argv[] )
{

        int descriptor ;
        int connection = -1 ;
        std::string response = "Hello From the Server" ;
        char buffer[BUFFERSIZE] ;
        sockaddr_in address ;

        createUDPClient( &descriptor ) ;

        

        auto addressLength = sizeof(address) ;

        while(connection == -1){
                connection = accept( descriptor, ( struct sockaddr* )&address, (socklen_t*)&addressLength) ;
        }

        read(connection, buffer, 30) ;

        std::cout << "Server Received: " << buffer ;

        send(connection, response.c_str(), response.size(), 0 ) ;

        close(connection) ;

        close(descriptor) ;

        return 0 ;
}

