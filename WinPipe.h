//
// Created by maste on 2025/11/28.
//

#ifndef RANGEHOODREADER_WINPIPE_H
#define RANGEHOODREADER_WINPIPE_H

#include "SerialReader.h"

class WinPipe
{
    HANDLE hPipe;
    const char* pipe_name;
    bool isOpen;

public:
    WinPipe() : hPipe(nullptr), isOpen(false), pipe_name(nullptr) {}
    ~WinPipe();
    bool open(const char* pipe_name);
    void send(const char* buffer, int length);
};

#endif //RANGEHOODREADER_WINPIPE_H