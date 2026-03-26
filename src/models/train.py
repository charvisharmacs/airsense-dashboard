import os
import sys
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 🔧 Add project root and src to Python path so `python src/models/train.py` works
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from src.data.preprocess import clean_data, create_rhri, classify_rhri
from src.features.feature_engineering import create_features
from src.config import set_seed

from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    roc_curve,
    auc
)

from sklearn.model_selection import (
    TimeSeriesSplit,
    RandomizedSearchCV,
    cross_val_score,
)
from sklearn.utils.class_weight import compute_class_weight

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


# ------------------------------------------------
# Evaluation + Plots
# ------------------------------------------------
def evaluate_and_plot(name, model, X_test, y_test, feature_names):
    """
    Compute core classification metrics and generate plots for a fitted model.

    Metrics:
      - Accuracy, weighted F1, weighted precision, weighted recall
    Plots:
      - Confusion matrix
      - One-vs-rest ROC curves (multi-class)
      - Feature importance (for tree-based models exposing feature_importances_)
    """

    os.makedirs("results", exist_ok=True)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    precision = precision_score(y_test, y_pred, average="weighted")
    recall = recall_score(y_test, y_pred, average="weighted")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)

    plt.figure()
    plt.imshow(cm)
    plt.title(f"{name} Confusion Matrix")
    plt.colorbar()
    plt.savefig(f"results/{name}_confusion_matrix.png")
    plt.close()

    # ROC Curve (one-vs-rest, assumes labels {0,1,2})
    y_test_bin = label_binarize(y_test, classes=[0, 1, 2])

    plt.figure()
    for i in range(y_test_bin.shape[1]):
        fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"Class {i} AUC={roc_auc:.2f}")

    plt.plot([0, 1], [0, 1])
    plt.legend()
    plt.title(f"{name} ROC Curve")
    plt.savefig(f"results/{name}_roc_curve.png")
    plt.close()

    # Feature Importance
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        indices = np.argsort(importances)[-15:]

        plt.figure()
        plt.barh(range(len(indices)), importances[indices])
        plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
        plt.title(f"{name} Feature Importance")
        plt.tight_layout()
        plt.savefig(f"results/{name}_feature_importance.png")
        plt.close()

    return {
        "Model": name,
        "Accuracy": accuracy,
        "F1": f1,
        "Precision": precision,
        "Recall": recall,
    }


# ------------------------------------------------
# Main Training
# ------------------------------------------------
def train_all_models(data_path):

    set_seed()

    df = pd.read_csv(data_path)

    df = clean_data(df)
    df = create_rhri(df)
    df = classify_rhri(df)
    df = create_features(df)

    print("After preprocessing:", df.shape)

    # sort chronologically if possible
    if "City" in df.columns and "Date" in df.columns:
        df = df.sort_values(["City", "Date"])

    X = df.drop(columns=[
        "Respiratory_Risk",
        "Risk_Percentage",
        "RHRI",
        "City",
        "Date",
        "PM2.5", "PM10", "NO2", "SO2", "O3", "CO",
        "PM2.5_norm", "PM10_norm", "NO2_norm",
        "SO2_norm", "O3_norm", "CO_norm"
    ], errors="ignore")

    X = X.select_dtypes(include=["number"])
    X = X.fillna(0)

    y = df["Respiratory_Risk"]

    # ------------------------------------------------
    # Class balance diagnostics + class weights
    # ------------------------------------------------
    class_counts = y.value_counts().sort_index()
    print("\nClass distribution (Respiratory_Risk):")
    print(class_counts)

    classes = class_counts.index.to_numpy()
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y.to_numpy()
    )
    class_weight_dict = {cls: w for cls, w in zip(classes, class_weights)}
    print("\nComputed class weights:")
    print(class_weight_dict)

    feature_names = X.columns.tolist()

    os.makedirs("models", exist_ok=True)
    joblib.dump(feature_names, "models/feature_names.pkl")

    split = int(len(X) * 0.8)

    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    joblib.dump(scaler, "models/scaler.pkl")

    results = []
    cv_results = []

    tscv = TimeSeriesSplit(n_splits=5)

    # ------------------------------------------------
    # XGBoost with lightweight hyperparameter tuning (TimeSeriesSplit)
    # ------------------------------------------------
    xgb_base = XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=42,
        tree_method="hist",
        n_jobs=-1,
    )

    # Small search space keeps runtime manageable while still
    # exploring a few sensible configurations.
    xgb_param_dist = {
        "n_estimators": [150, 250, 350],
        "max_depth": [3, 5, 7],
        "learning_rate": [0.03, 0.1],
        "min_child_weight": [1, 5],
        "subsample": [0.8, 1.0],
        "colsample_bytree": [0.8, 1.0],
    }

    xgb_search = RandomizedSearchCV(
        estimator=xgb_base,
        param_distributions=xgb_param_dist,
        n_iter=8,
        scoring="f1_weighted",
        n_jobs=1,
        cv=tscv,
        verbose=1,
        random_state=42,
        refit=True,
    )

    # Use sample weights to incorporate class imbalance for XGBoost
    sample_weight = y_train.map(class_weight_dict).to_numpy()
    xgb_search.fit(X_train_scaled, y_train, sample_weight=sample_weight)

    xgb_best = xgb_search.best_estimator_
    print("\nBest XGBoost params:")
    print(xgb_search.best_params_)

    scores = cross_val_score(
        xgb_best,
        X_train_scaled,
        y_train,
        cv=tscv,
        scoring="f1_weighted",
        n_jobs=1,
    )

    cv_results.append(["XGBoost", scores.mean()])

    joblib.dump(xgb_best, "models/xgb_model.pkl")

    results.append(
        evaluate_and_plot("XGBoost", xgb_best, X_test_scaled, y_test, feature_names)
    )

    # ------------------------------------------------
    # Random Forest (fixed, reasonably strong configuration)
    # ------------------------------------------------
    rf_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
        class_weight=class_weight_dict,
    )

    rf_model.fit(X_train_scaled, y_train)

    scores = cross_val_score(
        rf_model,
        X_train_scaled,
        y_train,
        cv=tscv,
        scoring="f1_weighted",
        n_jobs=1,
    )

    cv_results.append(["Random Forest", scores.mean()])

    joblib.dump(rf_model, "models/random_forest.pkl")

    results.append(
        evaluate_and_plot("Random Forest", rf_model, X_test_scaled, y_test, feature_names)
    )

    # Logistic Regression (with class weights)
    lr = LogisticRegression(max_iter=1000, class_weight=class_weight_dict)

    lr.fit(X_train_scaled, y_train)

    scores = cross_val_score(lr, X_train_scaled, y_train, cv=tscv)

    cv_results.append(["Logistic Regression", scores.mean()])

    joblib.dump(lr, "models/logistic_regression.pkl")

    results.append(
        evaluate_and_plot("Logistic Regression", lr, X_test_scaled, y_test, feature_names)
    )

    # Save results
    results_df = pd.DataFrame(results)

    os.makedirs("results", exist_ok=True)

    results_df.to_csv(
        "results/model_comparison.csv",
        index=False
    )

    cv_df = pd.DataFrame(
        cv_results,
        columns=["Model", "CV_Mean"]
    )

    cv_df.to_csv(
        "results/cross_validation_scores.csv",
        index=False
    )

    print("\nModel Comparison:")
    print(results_df)

    print("\nCross Validation Scores:")
    print(cv_df)


if __name__ == "__main__":

    train_all_models(
        "data/processed/final_with_weather.csv"
    )