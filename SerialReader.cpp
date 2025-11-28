#include "SerialReader.h"



bool SerialReader::connect(const char* port, DWORD baud)
{
    hSerial = CreateFile(port, GENERIC_READ, 0, nullptr,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (hSerial == INVALID_HANDLE_VALUE)
    {
        cerr << "Error opening serial port." << endl;
        return false;
    }

    DCB dcbSerialParams = {0};
    dcbSerialParams.DCBlength = sizeof(dcbSerialParams);

    if (!GetCommState(hSerial, &dcbSerialParams))
    {
        cerr << "Error getting serial port parameters." << endl;
        CloseHandle(hSerial);
        return false;
    }

    dcbSerialParams.BaudRate = baud;
    dcbSerialParams.ByteSize = 8;
    dcbSerialParams.StopBits = ONESTOPBIT;
    dcbSerialParams.Parity = NOPARITY;

    COMMTIMEOUTS timeouts = {0};
    timeouts.ReadIntervalTimeout = 50;
    timeouts.ReadTotalTimeoutConstant = 1000;
    timeouts.ReadTotalTimeoutMultiplier = 0;

    if (!SetCommState(hSerial, &dcbSerialParams) || !SetCommTimeouts(hSerial, &timeouts))
    {
        cerr << "Error setting serial port parameters." << endl;
        CloseHandle(hSerial);
        return false;
    }

    cerr << "Connected to " << port << endl;
    isConnected = true;
    return true;
}


string SerialReader::read()
{
    if (!isConnected)
    {
        cerr << "SerialReader is not connected." << endl;
        return "";
    }
    char buffer[BUFFER_SIZE];
    DWORD bytesRead;

    if (!ReadFile(hSerial, buffer, BUFFER_SIZE, &bytesRead, nullptr))
    {
        cerr << "Error reading from serial port." << endl;
        CloseHandle(hSerial);
        return "";
    }
    string result;
    if (bytesRead > 0)
    {
        result = string(buffer, bytesRead);
    }
    return result;
}


SerialReader::~SerialReader()
{
    if (isConnected)
    {
        CloseHandle(hSerial);
    }
}
