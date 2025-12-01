from pydub import AudioSegment
import os

input_folder = r"C:\Users\shuqi\UofT\MIE1050\Project\data_wav\not_sliced"
output_folder = r"C:\Users\shuqi\UofT\MIE1050\Project\data_chunks_5s"

os.makedirs(output_folder, exist_ok=True)

chunk_len = 5000  # ms

for file in os.listdir(input_folder):
    if file.endswith(".wav"):
        name = file[:-4]
        wav_path = os.path.join(input_folder, file)
        sound = AudioSegment.from_wav(wav_path)
        length = len(sound)

        chunk_folder = os.path.join(output_folder, name)
        os.makedirs(chunk_folder, exist_ok=True)

        for i in range(0, length, chunk_len):
            chunk = sound[i:i + chunk_len]
            out_path = os.path.join(chunk_folder, f"{name}_{i//1000}.wav")
            chunk.export(out_path, format="wav")

        print("Sliced:", name)
