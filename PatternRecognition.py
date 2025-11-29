import sys
import win32pipe
import win32file
import json
import csv
import os

from collections import Counter
from knn_detection import load_knn_model, predict_from_sensors


def save_sensor_to_csv(sensor_data, csv_path="sensor_log.csv"):
    """
    Save one sensor_data dict into a CSV file.
    If the file does not exist, create it and write the header.
    Each key becomes a column; each call appends one row.
    """

    # Extract the column names from dict keys
    fieldnames = list(sensor_data.keys())

    # Check if file exists
    file_exists = os.path.isfile(csv_path)

    # Open file for append
    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # If first time, write header
        if not file_exists:
            writer.writeheader()

        # Write one row
        writer.writerow(sensor_data)


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
    result, data = win32file.ReadFile(named_pipe, pipe_buffer)
    if result == 0:
        # decode bytes into string
        message = data.decode('utf-8').rstrip('\x00')
        return message
    return None


if __name__ == "__main__":
    print("\nRunning Pattern Recognition")
    
    try:
        knn_model = load_knn_model("knn_cooking_model.pkl")
        print("Loaded KNN model.")
    except Exception as e:
        print("Failed to load KNN model:", e)
        sys.exit(1)

    pipe_name = "\\\\.\\pipe\\test_pipe"
    pipe_buffer_size = 512

    # For 5-second voting
    prediction_buffer = []
    current_status = None

    while True :
        # create named pipe
        named_pipe = win32pipe.CreateNamedPipe(
            pipe_name,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT | win32pipe.PIPE_READMODE_MESSAGE,
            win32pipe.PIPE_UNLIMITED_INSTANCES,
            pipe_buffer_size,
            pipe_buffer_size,
            0,
            None
        )

        try:
            if named_pipe:
                print("Waiting for connection...")
                win32pipe.ConnectNamedPipe(named_pipe, None)
                print("Connected to C++ client")

                while True:

                    data = receive(named_pipe, pipe_buffer_size)
                    if data:
                        try:
                            # load json data
                            sensor_data = json.loads(data)
                            #print_sensor_data(sensor_data)
                            #save_sensor_to_csv(sensor_data)
                            temp = float(sensor_data["temperature"])
                            rh = float(sensor_data["humidity"])
                            distance = float(sensor_data["us_raw"])
                            air_quality = float(sensor_data["gas"])

                            label, conf = predict_from_sensors(
                                temp=temp,
                                rh=rh,
                                distance=distance,
                                air_quality=air_quality,
                                model_path="knn_cooking_model.pkl"
                            )
                            print(f"[1-sec KNN] {label} (conf={conf:.2f})")

                            prediction_buffer.append(label)

                            # ====== Every 5 readings → voting ======
                            if len(prediction_buffer) >= 5:
                                counts = Counter(prediction_buffer)
                                voted_label, vote_count = counts.most_common(1)[0]

                                current_status = voted_label
                                print(f"[5-sec vote] Final Status = {current_status}  |  Votes = {dict(counts)}")

                                prediction_buffer.clear()
                            print("-" * 50)
                            
                        except json.JSONDecodeError:
                            print("Raw message:", data)
                        print("-" * 50)
        except KeyboardInterrupt:
            print("Keyboard interrupt. Exiting...")
            print("Exit Pattern Recognition")
            if named_pipe:
                win32pipe.DisconnectNamedPipe(named_pipe)
                win32file.CloseHandle(named_pipe)
            sys.exit(0)
        except Exception as e:
            print("Pipe closed. Try to reopen...")
            continue