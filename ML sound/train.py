import os
import glob
import numpy as np
import librosa

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
import argparse

# ====== Your data path ======
DATA_DIR = r"C:\Users\shuqi\UofT\MIE1050\Project\sound_data"
SAMPLE_RATE = 16000  # keep consistent across training / inference


def extract_features(file_path: str) -> np.ndarray:
    """
    Extract features from a single wav file:
    - load mono audio
    - compute MFCC
    - take mean and std over time axis -> fixed-length vector
    """
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)

    # simple amplitude normalization
    if np.max(np.abs(y)) > 0:
        y = y / np.max(np.abs(y))

    # 20-dim MFCC is enough here
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)

    # mean and std along time axis
    mfcc_mean = mfcc.mean(axis=1)
    mfcc_std = mfcc.std(axis=1)

    features = np.concatenate([mfcc_mean, mfcc_std])  # length = 40
    return features


def load_dataset(data_dir: str):
    """
    Walk through each subfolder under data_dir:
      subfolder name = class name (e.g., boiling / searing / stirfrying)
      all wav files inside that subfolder are treated as that class.
    Returns:
      X: np.ndarray, shape (N_samples, N_features)
      y_str: list of string labels (class names for each sample)
      class_names: sorted list of unique class names
    """
    X = []
    y_str = []
    class_names = []

    # use sorted() so class order is stable
    for class_name in sorted(os.listdir(data_dir)):
        class_path = os.path.join(data_dir, class_name)
        if not os.path.isdir(class_path):
            continue

        class_names.append(class_name)
        wav_files = glob.glob(os.path.join(class_path, "*.wav"))
        print(f"Found {len(wav_files)} files in class '{class_name}'")

        for wav_path in wav_files:
            try:
                feat = extract_features(wav_path)
                X.append(feat)
                y_str.append(class_name)  # keep string label here
            except Exception as e:
                print(f"[WARN] Failed on {wav_path}: {e}")

    X = np.array(X)
    y_str = np.array(y_str)
    return X, y_str, class_names


def train_model():
    X, y_str, class_names = load_dataset(DATA_DIR)

    print("Total samples:", len(X))
    if len(X) < 10:
        print("Dataset is quite small; results may be unstable, but let's run it first.")

    # encode string labels -> integers using LabelEncoder
    le = LabelEncoder()
    y = le.fit_transform(y_str)

    # split train / test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Random Forest classifier
    rf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    # use le.classes_ as target names, it matches encoded labels
    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # save model + label encoder + sample rate
    model_obj = {
        "rf": rf,                  # RandomForest model
        "label_encoder": le,       # LabelEncoder for mapping <-> class names
        "sample_rate": SAMPLE_RATE
    }
    joblib.dump(model_obj, "sound_model.pkl")
    print("\nModel saved to sound_model.pkl")


def predict_one(model_path: str, wav_path: str):
    """
    Load a trained model and run prediction on a single wav file.
    """
    model_obj = joblib.load(model_path)
    rf = model_obj["rf"]
    le = model_obj["label_encoder"]

    feat = extract_features(wav_path).reshape(1, -1)
    pred_int = rf.predict(feat)[0]
    proba = rf.predict_proba(feat)[0]

    # convert integer label back to string class name
    pred_label = le.inverse_transform([pred_int])[0]
    class_names = le.classes_

    print(f"File: {wav_path}")
    print(f"Predicted class: {pred_label}")
    for idx, name in enumerate(class_names):
        print(f"  {name:12s}: {proba[idx]:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--predict",
        type=str,
        help="Path to a wav file to classify. If not set, will train the model."
    )
    args = parser.parse_args()

    if args.predict:
        predict_one("sound_model.pkl", args.predict)
    else:
        train_model()
