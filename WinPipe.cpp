#include "WinPipe.h"

bool WinPipe::open(const char* pipeName)
{
    int retry_count = 0;
    const int max_retries = INT_MAX;
    pipe_name = pipeName;
    isOpen = false;

    cerr << "Waiting for patter recognition service to start..." << endl;
    while (retry_count < max_retries)
    {
        if (WaitNamedPipe(pipeName, NMPWAIT_WAIT_FOREVER))
        {
            hPipe = CreateFile(pipeName, GENERIC_WRITE, 0,
                nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL,
                nullptr);
            if (hPipe == INVALID_HANDLE_VALUE)
            {
                cerr << "Failed to open pipe" << endl;
                isOpen = false;
                return false;
            }
            isOpen = true;
            break;
        }
        retry_count++;
        Sleep(1000);
    }
    return isOpen;
}


void WinPipe::send(const char* buffer, int length)
{
    DWORD bytesWritten;
    if (WriteFile(hPipe, buffer, length, &bytesWritten, nullptr))
    {
        cout << "Sent data to Pipeline" << endl;
    } else
    {
        cerr << "Pipeline closed. Try to reopen..." << endl;
        this->open(pipe_name);
        cerr << "Pipeline created. Sending sensor data..." << endl;
    }
}


WinPipe::~WinPipe()
{
    if (isOpen)
    {
        CloseHandle(hPipe);
    }
}