#ifndef RANGEHOODREADER_SERIALREADER_H
#define RANGEHOODREADER_SERIALREADER_H

#include <string>
#include <windows.h>
#include <iostream>
using namespace std;

#define BUFFER_SIZE 512

class SerialReader
{
    HANDLE hSerial;
    bool isConnected;

public:
    SerialReader() : hSerial(nullptr), isConnected(false)
    {
    }

    ~SerialReader();

    bool connect(const char* port, DWORD baud = 115200);
    string read();
};

#endif //RANGEHOODREADER_SERIALREADER_H

