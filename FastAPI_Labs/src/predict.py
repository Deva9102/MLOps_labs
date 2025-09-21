import joblib
import numpy as np

def predict_data(features):
    """
    Predict the class labels for the input data.
    Args:
        X (numpy.ndarray): Input data for which predictions are to be made.
    Returns:
        y_pred (numpy.ndarray): Predicted class labels.
    """
    model = joblib.load("../model/digits_model.pkl")
    X = np.asarray(features, dtype=float).reshape(1, -1)
    return model.predict(X)
