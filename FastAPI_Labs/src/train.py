from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import joblib
from data import load_data, split_data

def fit_model(X_train, y_train, X_test, y_test):
    """
    Train SVM classifier on the Digits dataset and save the model to a pkl file.
    Args:
        X_train (numpy.ndarray): Training features (n_samples, 64).
        y_train (numpy.ndarray): Training labels (n_samples,).
        X_test  (numpy.ndarray): Test features.
        y_test  (numpy.ndarray): Test labels.
    """
    svm_classifier = SVC(kernel="rbf", gamma=0.001, C=10)
    svm_classifier.fit(X_train, y_train)

    # Evaluate the model
    y_pred = svm_classifier.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("=" * 50)
    print(f"Test Accuracy: {acc:.4f}")
    print("\n Classification Report:")
    print(classification_report(y_test, y_pred, digits=3))
    print("=" * 50)

    joblib.dump(svm_classifier, "../model/digits_model.pkl")

if __name__ == "__main__":
    X, y = load_data()
    X_train, X_test, y_train, y_test = split_data(X, y)
    fit_model(X_train, y_train, X_test, y_test)
