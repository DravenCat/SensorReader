import sys
import win32pipe
import win32file
import struct
import json

def print_sensor_data(sensor_data):
    print(f"Temp: {sensor_data['temperature']} `C")
    print(f"Hum: {sensor_data['humidity']} %")
    print(f"Pres: {sensor_data['pressure']} kPa")
    print(f"Gas: {sensor_data['gas']} kOhms")
    print(f"Alt: {sensor_data['altitude']} m")
    print(f"Xg: {sensor_data['xg']} g")
    print(f"Yg: {sensor_data['yg']} g")
    print(f"Zg: {sensor_data['zg']} g")
    print(f"Mic: {sensor_data['mic']} ({sensor_data['vMic']} V)")
    print(f"EMF: {sensor_data['emf']} ({sensor_data['vEmf']} V)")
    print(f"Light: {sensor_data['light']} ({sensor_data['vLight']} V)")
    print(f"AIN: {sensor_data['ain']} ({sensor_data['vAin']} V)")
    print(f"US Raw: {sensor_data['us_raw']} mm")
    print(f"US Compensated: {sensor_data['us_compensated']} mm")
    print(f"Time of Flight: {sensor_data['time_of_flight']} ns")

def receive(named_pipe, pipe_buffer):
    try:
        # 读取数据
        result, data = win32file.ReadFile(named_pipe, pipe_buffer)
        if result == 0:
            # 解码字节数据为字符串
            message = data.decode('utf-8').rstrip('\x00')
            return message
        return None
    except Exception as e:
        print(f"Read error: {e}")
        return None

if __name__ == "__main__":
    print("\nRunning Pattern Recognition")
    pipe_name = "\\\\.\\pipe\\test_pipe"
    pipe_buffer = 512

    try:
        # 创建命名管道
        named_pipe = win32pipe.CreateNamedPipe(
            pipe_name,
            win32pipe.PIPE_ACCESS_DUPLEX,  # 改为双向以匹配C++端
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT | win32pipe.PIPE_READMODE_MESSAGE,
            win32pipe.PIPE_UNLIMITED_INSTANCES,
            pipe_buffer,
            pipe_buffer,
            0,  # 改为0表示无限等待
            None
        )

        if named_pipe:
            print("Waiting for connection...")
            # 等待连接
            win32pipe.ConnectNamedPipe(named_pipe, None)
            print("Connected to C++ client")

            while True:
                data = receive(named_pipe, pipe_buffer)
                if data:
                    print("Received raw data:", data)

                    # 尝试解析JSON数据
                    try:
                        sensor_data = json.loads(data)
                        print_sensor_data(sensor_data)
                    except json.JSONDecodeError:
                        # 如果不是JSON，直接打印原始数据
                        print("Raw message:", data)
                    print("-" * 50)

    except KeyboardInterrupt:
        print("\nExiting Pattern Recognition")
    finally:
        # 清理资源
        if 'named_pipe' in locals():
            win32pipe.DisconnectNamedPipe(named_pipe)
            win32file.CloseHandle(named_pipe)
        sys.exit(0)