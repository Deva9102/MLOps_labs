import os
import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Load data from a CSV file
def load_data():
    """
    Loads the Breast Cancer dataset CSV from:
      ~/airflow/dags/data/breast_cancer.csv
    Returns:
        pd.DataFrame
    """
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "breast_cancer.csv")
    data = pd.read_csv(csv_path)
    return data

# Preprocess the data
def data_preprocessing(data):
    # Expect a 'target' column (0/1). All other columns are numeric features.
    X = data.drop(['target'], axis=1)
    y = data['target'].astype(int)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train.values, y_test.values

# Build and save a Random Forest model (+ print metrics)
def build_model(data, filename):
    X_train, X_test, y_train, y_test = data

    # Train RandomForest
    rf_clf = RandomForestClassifier(n_estimators=300, max_depth=None, random_state=42)
    rf_clf.fit(X_train, y_train)

    # Metrics
    y_pred = rf_clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    print(f"Metrics -> accuracy: {acc:.4f}, precision: {prec:.4f}, recall: {rec:.4f}")

    # Save model
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    pickle.dump(rf_clf, open(output_path, 'wb'))

# Load a saved model and evaluate (optional)
def load_model(data, filename):
    X_train, X_test, y_train, y_test = data
    output_path = os.path.join(os.path.dirname(__file__), "../model", filename)

    loaded_model = pickle.load(open(output_path, 'rb'))
    predictions = loaded_model.predict(X_test)
    print(f"Model score (accuracy) on test data: {loaded_model.score(X_test, y_test):.4f}")

    return predictions[0]

if __name__ == '__main__':
    x = load_data()
    x = data_preprocessing(x)
    build_model(x, 'model.sav')
