"""
Multi-Model Supervised Training & Validation Engine (XGBoost, Random Forest, SVM)
Greater Accra Metropolitan Area (GAMA), Ghana
Emmanuel Yerbo | GeoAI & Remote Sensing Engineering
"""

import os
import argparse
import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, cohen_kappa_score, classification_report,
    confusion_matrix, f1_score
)
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from dataset import load_and_preprocess_dataset, CLASS_NAMES


def train_and_evaluate_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series
) -> Dict[str, Dict[str, Any]]:
    """
    Trains and benchmarks Random Forest, Support Vector Machine, and XGBoost classifiers.
    """
    target_names = [CLASS_NAMES[i] for i in sorted(CLASS_NAMES.keys())]
    results = {}

    # 1. Random Forest Classifier
    print("\n[1/3] Training Random Forest Ensemble (100 estimators)...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    rf_kappa = cohen_kappa_score(y_test, rf_preds)
    rf_f1 = f1_score(y_test, rf_preds, average='weighted')
    results['Random Forest'] = {
        'model': rf,
        'accuracy': rf_acc,
        'kappa': rf_kappa,
        'f1': rf_f1,
        'preds': rf_preds,
        'cm': confusion_matrix(y_test, rf_preds)
    }

    # 2. Support Vector Machine (RBF Kernel with Standardized Features)
    print("\n[2/3] Training Support Vector Classifier (RBF Kernel)...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    svm = SVC(kernel='rbf', C=10.0, gamma='scale', probability=True, random_state=42)
    svm.fit(X_train_scaled, y_train)
    svm_preds = svm.predict(X_test_scaled)
    svm_acc = accuracy_score(y_test, svm_preds)
    svm_kappa = cohen_kappa_score(y_test, svm_preds)
    svm_f1 = f1_score(y_test, svm_preds, average='weighted')
    results['SVM'] = {
        'model': svm,
        'scaler': scaler,
        'accuracy': svm_acc,
        'kappa': svm_kappa,
        'f1': svm_f1,
        'preds': svm_preds,
        'cm': confusion_matrix(y_test, svm_preds)
    }

    # 3. XGBoost Classifier
    print("\n[3/3] Training Extreme Gradient Boosting (XGBoost)...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss'
    )
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    xgb_acc = accuracy_score(y_test, xgb_preds)
    xgb_kappa = cohen_kappa_score(y_test, xgb_preds)
    xgb_f1 = f1_score(y_test, xgb_preds, average='weighted')
    results['XGBoost'] = {
        'model': xgb_model,
        'accuracy': xgb_acc,
        'kappa': xgb_kappa,
        'f1': xgb_f1,
        'preds': xgb_preds,
        'cm': confusion_matrix(y_test, xgb_preds)
    }

    # Print Summary Table
    print("\n" + "="*75)
    print(f"{'Algorithm':<20} | {'Overall Acc (OA)':<18} | {'Cohen Kappa':<15} | {'Weighted F1':<12}")
    print("="*75)
    for name, m in results.items():
        print(f"{name:<20} | {m['accuracy']*100:<17.2f}% | {m['kappa']:<15.4f} | {m['f1']:<12.4f}")
    print("="*75)

    # Detailed Classification Report for Winning Model
    best_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
    print(f"\nWinning Architecture: {best_name} (Acc: {results[best_name]['accuracy']*100:.2f}%)")
    print("\nDetailed Test Set Classification Report:")
    print(classification_report(y_test, results[best_name]['preds'], target_names=target_names, digits=4))
    print("Confusion Matrix:")
    print(results[best_name]['cm'])

    return results


def main():
    parser = argparse.ArgumentParser(description="Train GAMA LULC Classifiers")
    parser.add_argument("--data", type=str, default="data/XAI_TRAINING_DATASET.csv", help="Path to CSV dataset")
    parser.add_argument("--test_size", type=float, default=0.20, help="Test set fraction")
    args = parser.parse_args()

    default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "XAI_TRAINING_DATASET.csv")
    csv_path = args.data if os.path.exists(args.data) else default_path

    print(f"Loading GAMA LULC training dataset: {csv_path}")
    X_train, X_test, y_train, y_test, features = load_and_preprocess_dataset(csv_path, test_size=args.test_size)
    print(f"Features after multicollinearity pruning ({len(features)}): {features}")
    print(f"Train samples: {len(X_train)} | Test samples: {len(X_test)}")

    train_and_evaluate_models(X_train, X_test, y_train, y_test)


if __name__ == "__main__":
    main()
