#include "WinPipe.h"

bool WinPipe::open(const char* pipeName)
{
    if (WaitNamedPipe(pipeName, NMPWAIT_WAIT_FOREVER))
    {
        hPipe = CreateFile(pipeName, GENERIC_WRITE, 0,
            nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL,
            nullptr);
        if (hPipe == INVALID_HANDLE_VALUE)
        {
            cerr << "Failed to open pipe" << endl;
            return false;
        }
    }
    isOpen = true;
    return true;
}


void WinPipe::send(const char* buffer)
{
    DWORD bytesWritten;
    if (WriteFile(hPipe, buffer, BUFFER_SIZE, &bytesWritten, nullptr))
    {
        cout << "Sent data to Pipeline" << endl;
    } else
    {
        cerr << "Failed to send data to Pipeline" << endl;
    }
}


WinPipe::~WinPipe()
{
    if (isOpen)
    {
        CloseHandle(hPipe);
    }
}