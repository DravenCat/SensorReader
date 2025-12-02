
from pydub import AudioSegment
import os

input_folder = r"C:\Users\shuqi\UofT\MIE1050\Project\data_m4a"
output_folder = r"C:\Users\shuqi\UofT\MIE1050\Project\data_wav"

os.makedirs(output_folder, exist_ok=True)

for file in os.listdir(input_folder):
    if file.endswith(".m4a"):
        name = file[:-4]
        m4a_path = os.path.join(input_folder, file)
        wav_path = os.path.join(output_folder, name + ".wav")

        audio = AudioSegment.from_file(m4a_path, format="m4a")
        audio = audio.set_frame_rate(16000).set_channels(1)  # ML常用格式：16kHz + mono
        audio.export(wav_path, format="wav")

        print("Converted:", wav_path)
