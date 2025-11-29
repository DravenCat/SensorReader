import numpy as np
import pandas as pd
from collections import Counter
import pickle

# ======= Configuration =======
# Column names in your CSV file
FEATURES = ["temperature", "humidity", "us_raw", "gas"]  # change if needed
LABEL_COL = "status"  # the column with "cooking nearby"/"not cooking"/"cooking away"

# Path to save the trained KNN "model"
MODEL_PATH = "knn_cooking_model.pkl"


# ======= Helper functions =======

def normalize_features(X, xmin=None, xmax=None):
    """
    Min-max normalization: (x - xmin) / (xmax - xmin)
    If xmin and xmax are None, they will be computed from X.
    Returns normalized X, xmin, xmax.
    """
    if xmin is None:
        xmin = X.min(axis=0)
    if xmax is None:
        xmax = X.max(axis=0)

    # Avoid division by zero by adding a small epsilon
    X_norm = (X - xmin) / (xmax - xmin + 1e-8)
    return X_norm, xmin, xmax


def euclidean_distance(a, b):
    """
    Compute Euclidean distance between two vectors.
    """
    return np.linalg.norm(a - b)


def knn_predict(X_train, y_train, X_test, k=5):
    """
    Simple KNN classifier.
    X_train: 2D array of training samples (normalized).
    y_train: 1D array of training labels.
    X_test:  2D array of test samples (normalized).
    k:       number of neighbors.

    Returns:
        predictions: array of predicted labels
        confidences: array of confidence scores (majority ratio)
    """
    predictions = []
    confidences = []

    for test_point in X_test:
        # Compute distance from test_point to all training points
        distances = [euclidean_distance(test_point, x) for x in X_train]

        # Indices of the k nearest neighbors
        k_indices = np.argsort(distances)[:k]
        k_labels = [y_train[i] for i in k_indices]

        # Majority vote
        counts = Counter(k_labels)
        most_common_label, count = counts.most_common(1)[0]
        confidence = count / k

        predictions.append(most_common_label)
        confidences.append(confidence)

    return np.array(predictions), np.array(confidences)


def train_and_save_knn(csv_path, k=5, model_path=MODEL_PATH):
    """
    Train KNN on the full labeled dataset and save the "model" information.
    The model here is simply:
        - normalized training features
        - labels
        - min and max for each feature (for normalization)
        - k value
    """
    # Read data
    df = pd.read_csv(csv_path)

    # Extract features and labels
    X = df[FEATURES].values.astype(float)
    y = df[LABEL_COL].values

    # Normalize features
    X_norm, xmin, xmax = normalize_features(X)

    # Pack everything into a dictionary
    model = {
        "X_train": X_norm,
        "y_train": y,
        "xmin": xmin,
        "xmax": xmax,
        "k": k,
        "features": FEATURES,
    }

    # Save model to disk
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    print(f"Model trained with {len(y)} samples and saved to: {model_path}")


def load_knn_model(model_path=MODEL_PATH):
    """
    Load the saved KNN model dictionary from disk.
    """
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model


def predict_from_sensors(temp, rh, distance, air_quality, model_path=MODEL_PATH):
    """
    Load the saved KNN model and predict the cooking status
    for one new sensor reading.

    Returns:
        predicted_label: one of "cooking nearby"/"not cooking"/"cooking away"
        confidence:      majority ratio (0~1)
    """
    model = load_knn_model(model_path)

    X_train = model["X_train"]
    y_train = model["y_train"]
    xmin = model["xmin"]
    xmax = model["xmax"]
    k = model["k"]

    # Build a 2D array for a single sample
    new_sample = np.array([[temp, rh, distance, air_quality]], dtype=float)

    # Normalize using training xmin/xmax
    new_sample_norm, _, _ = normalize_features(new_sample, xmin, xmax)

    # Use the same KNN function as before
    pred, conf = knn_predict(X_train, y_train, new_sample_norm, k=k)

    return pred[0], conf[0]


# ======= Example usage =======
if __name__ == "__main__":
    # 1) First: train and save the model
    #    Change this path to your own CSV file path.
    csv_path = r"C:\Users\shuqi\UofT\MIE1050\Project\sensor_log.csv"
    train_and_save_knn(csv_path, k=5, model_path=MODEL_PATH)

    # 2) Later (or in another script), you can call predict_from_sensors(...)
    #    Here is just a demo example:
    example_temp = 24.5
    example_rh = 45.0
    example_distance = 1.2
    example_air_quality = 36.0

    label, conf = predict_from_sensors(
        temp=example_temp,
        rh=example_rh,
        distance=example_distance,
        air_quality=example_air_quality,
        model_path=MODEL_PATH
    )

    print(f"Predicted status: {label}, confidence: {conf:.2f}")
