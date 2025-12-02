import time
import numpy as np
import sounddevice as sd
import librosa
import joblib

MODEL_PATH = "sound_model.pkl"
WINDOW_SECONDS = 3.0          # length of each audio window in seconds
SAMPLE_RATE = 16000           # training rate
N_MFCC = 20
CONF_THRESHOLD = 0.6          # if max probability < threshold -> treat as Unknown


def extract_features_from_raw(y: np.ndarray, sr: int) -> np.ndarray:
    """
    Extract MFCC-based features from a raw audio array.
    This must match the preprocessing used in train.py.
    """
    # Ensure mono 1D
    if y.ndim > 1:
        y = y[:, 0]

    # Amplitude normalization
    if np.max(np.abs(y)) > 0:
        y = y / np.max(np.abs(y))

    # Compute MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)

    # Mean + std along time axis
    mfcc_mean = mfcc.mean(axis=1)
    mfcc_std = mfcc.std(axis=1)

    features = np.concatenate([mfcc_mean, mfcc_std])  # length = 2 * N_MFCC
    return features


def main():
    # Load trained model object
    model_obj = joblib.load(MODEL_PATH)

    # RandomForest model
    rf = model_obj["rf"]
    # LabelEncoder used during training
    le = model_obj["label_encoder"]
    # The sample rate used in training (for sanity check)
    sr_model = model_obj.get("sample_rate", SAMPLE_RATE)

    if sr_model != SAMPLE_RATE:
        print(f"[WARN] MODEL sample_rate={sr_model}, but we use {SAMPLE_RATE}")

    # Class names are stored inside the LabelEncoder
    class_names = le.classes_

    print("=== Real-time cooking sound detection ===")

    try:
        while True:
            # Record one audio window
            frames = int(WINDOW_SECONDS * SAMPLE_RATE)
            audio = sd.rec(
                frames,
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32"
            )
            sd.wait()  # wait until recording is finished

            y = audio.squeeze()
            feat = extract_features_from_raw(y, SAMPLE_RATE).reshape(1, -1)

            # Predict probabilities with RF
            proba = rf.predict_proba(feat)[0]
            pred_idx = int(np.argmax(proba))          # integer class index
            confidence = float(proba[pred_idx])

            # Map index -> string label using LabelEncoder
            pred_label = le.inverse_transform([pred_idx])[0]

            timestamp = time.strftime("%H:%M:%S")
            if confidence < CONF_THRESHOLD:
                print(f"{timestamp}  ->  Unknown / silence  (max p={confidence:.2f})")
            else:
                print(f"{timestamp}  ->  {pred_label:<12s} (p={confidence:.2f})")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()