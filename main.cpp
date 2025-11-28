#include "SerialReader.h"
#include "WinPipe.h"
#include <sstream>
#include <iomanip>


struct SensorData
{
    float temperature;
    float humidity;
    float pressure;
    float gas;
    float altitude;
    float xg;
    float yg;
    float zg;
    int mic;
    int emf;
    int light;
    int ain;
    float vMic;
    float vEmf;
    float vLight;
    float vAin;
    float us_raw;
    float us_compensated;
    double time_of_flight;

    SensorData() : temperature(0), humidity(0), pressure(0), gas(0), altitude(0), xg(0), yg(0), zg(0), mic(0), emf(0),
                   light(0), ain(0), vMic(0), vEmf(0), vLight(0), vAin(0),
                   us_raw(0),
                   us_compensated(0),
                   time_of_flight(0)
    {}
};


/***
 * Parse the raw sensor data from string into struct
 */
void parseData(const string &raw_data, SensorData &sensor_data)
{
    stringstream ss(raw_data);
    string line;

    while (getline(ss, line))
    {
        if (line.find("Temp") != string::npos)
        {
            sscanf(line.c_str(), "Temp:  %f", &sensor_data.temperature);
        }
        else if (line.find("Hum") != string::npos)
        {
            sscanf(line.c_str(), "Hum:   %f", &sensor_data.humidity);
        }
        else if (line.find("Pres") != string::npos)
        {
            sscanf(line.c_str(), "Pres:  %f", &sensor_data.pressure);
        }
        else if (line.find("Gas") != string::npos)
        {
            sscanf(line.c_str(), "Gas:   %f", &sensor_data.gas);
        }
        else if (line.find("Alt") != string::npos)
        {
            sscanf(line.c_str(), "Alt:   %f", &sensor_data.altitude);
        }
        else if (line.find("Xg") != string::npos)
        {
            sscanf(line.c_str(), "Xg:    %f", &sensor_data.xg);
        }
        else if (line.find("Yg") != string::npos)
        {
            sscanf(line.c_str(), "Yg:    %f", &sensor_data.yg);
        }
        else if (line.find("Zg") != string::npos)
        {
            sscanf(line.c_str(), "Zg:    %f", &sensor_data.zg);
        }
        else if (line.find("Mic") != string::npos)
        {
            sscanf(line.c_str(), "Mic:   %d (%f V)", &sensor_data.mic, &sensor_data.vMic);
        }
        else if (line.find("EMF") != string::npos)
        {
            sscanf(line.c_str(), "EMF:   %d (%f V)", &sensor_data.emf, &sensor_data.vEmf);
        }
        else if (line.find("Light") != string::npos)
        {
            sscanf(line.c_str(), "Light: %d (%f V)", &sensor_data.light, &sensor_data.vLight);
        }
        else if (line.find("AIN") != string::npos)
        {
            sscanf(line.c_str(), "AIN:   %d (%f V)", &sensor_data.ain, &sensor_data.vAin);
        }
        else if (line.find("US Raw") != string::npos)
        {
            sscanf(line.c_str(), "US Raw:    %f", &sensor_data.us_raw);
        }
        else if (line.find("US Compensated") != string::npos)
        {
            sscanf(line.c_str(), "US Compensated: %f", &sensor_data.us_compensated);
        }
        else if (line.find("Time of Flight") != string::npos)
        {
            sscanf(line.c_str(), "Time of Flight:   %lf", &sensor_data.time_of_flight);
        }
    }
}


/***
 * Print the sensor data
 */
void printData(const SensorData &sensor_data)
{
    cout << "Sensor Data: " << endl;
    cout << "Temp: " << fixed << setprecision(6) << sensor_data.temperature << " `C" << endl;
    cout << "Hum: " << fixed << setprecision(6) << sensor_data.humidity << " %" << endl;
    cout << "Pres: " << fixed << setprecision(6) << sensor_data.pressure << " kPa" << endl;
    cout << "Gas: " << fixed << setprecision(6) << sensor_data.gas << " kOhms" << endl;
    cout << "Alt: " << fixed << setprecision(6) << sensor_data.altitude << " m" << endl;
    cout << "Xg: " << fixed << setprecision(6) << sensor_data.xg << " g" << endl;
    cout << "Yg: " << fixed << setprecision(6) << sensor_data.yg << " g" << endl;
    cout << "Zg: " << fixed << setprecision(6) << sensor_data.zg << " g" << endl;
    cout << "Mic: " << sensor_data.mic << "(" << fixed << setprecision(6) << sensor_data.vMic << " V)" << endl;
    cout << "EMF: " << sensor_data.emf << "(" << fixed << setprecision(6) << sensor_data.vEmf << " V)" << endl;
    cout << "Light: " << sensor_data.light << "(" << fixed << setprecision(6) << sensor_data.vLight << " V)" << endl;
    cout << "AIN: " << sensor_data.ain << "(" << fixed << setprecision(6) << sensor_data.vAin << " V)" << endl;
    cout << "US Raw: " << fixed << setprecision(6) << sensor_data.us_raw << " mm" << endl;
    cout << "US Compensated: " << fixed << setprecision(6) << sensor_data.us_compensated << " mm" << endl;
    cout << "Time of Flight: " << fixed << setprecision(6) << sensor_data.time_of_flight << " ns" << endl;
}


/***
 * Convert sensor data to Json format
 */
string sensorDataToJson(const SensorData& data) {
    stringstream json;
    json << fixed << setprecision(6);
    json << "{";
    json << "\"temperature\":" << data.temperature << ",";
    json << "\"humidity\":" << data.humidity << ",";
    json << "\"pressure\":" << data.pressure << ",";
    json << "\"gas\":" << data.gas << ",";
    json << "\"altitude\":" << data.altitude << ",";
    json << "\"xg\":" << data.xg << ",";
    json << "\"yg\":" << data.yg << ",";
    json << "\"zg\":" << data.zg << ",";
    json << "\"mic\":" << data.mic << ",";
    json << "\"emf\":" << data.emf << ",";
    json << "\"light\":" << data.light << ",";
    json << "\"ain\":" << data.ain << ",";
    json << "\"vMic\":" << data.vMic << ",";
    json << "\"vEmf\":" << data.vEmf << ",";
    json << "\"vLight\":" << data.vLight << ",";
    json << "\"vAin\":" << data.vAin << ",";
    json << "\"us_raw\":" << data.us_raw << ",";
    json << "\"us_compensated\":" << data.us_compensated << ",";
    json << "\"time_of_flight\":" << data.time_of_flight;
    json << "}";
    return json.str();
}


[[noreturn]] int main()
{
    SerialReader reader;
    WinPipe pipe;
    const char* port = "COM4";
    const char* pipeName = R"(\\.\pipe\test_pipe)";

    if (reader.connect(port) && pipe.open(pipeName))
    {
        cerr << "Pipeline created. Sending sensor data..." << endl;
        while (true)
        {
            string raw_data = reader.read();
            if (!raw_data.empty())
            {
                SensorData sensor_data{};
                parseData(raw_data, sensor_data);
                string json_data = sensorDataToJson(sensor_data);
                pipe.send(json_data.c_str(), json_data.length()+1);
            }
        }

    } else
    {
        cerr << "Port " << port<<" unavailable. Check other port" << endl;
    }
}