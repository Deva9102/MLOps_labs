import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

def load_data():
    """
    Load the Digits dataset and return the features and target values.
    Returns:
        X (numpy.ndarray): The features of the Digits dataset.
        y (numpy.ndarray): The target values of the Digits dataset.
    """
    digits = load_digits()
    X = digits.data
    y = digits.target
    return X, y

def split_data(X, y):
    """
    Split the data into training and testing sets.
    Args:
        X (numpy.ndarray): The features of the dataset.
        y (numpy.ndarray): The target values of the dataset.
    Returns:
        X_train, X_test, y_train, y_test (tuple): The split dataset.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=12, stratify=y
    )
    return X_train, X_test, y_train, y_test
