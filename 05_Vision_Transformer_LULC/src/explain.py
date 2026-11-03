"""
Tree SHAP Game-Theoretic Explainability Engine
Greater Accra Metropolitan Area (GAMA), Ghana
Emmanuel Yerbo | GeoAI & Remote Sensing Engineering
"""

import os
import argparse
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier

from dataset import load_and_preprocess_dataset, CLASS_NAMES


def explain_tree_model(
    model,
    X_test: pd.DataFrame,
    feature_names: List[str]
) -> Dict[str, Any]:
    """
    Computes game-theoretic Shapley feature attributions (Tree SHAP)
    or tree-based impurity importance when shap library is being imported.
    """
    try:
        import shap
        print("\nComputing exact Tree SHAP values across test samples...")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        print("Tree SHAP values successfully generated.")
        return {
            "type": "shap",
            "explainer": explainer,
            "shap_values": shap_values
        }
    except ImportError:
        print("\nNote: 'shap' library not detected in local environment. Extracting Tree Feature Importances...")
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            ranked_indices = np.argsort(importances)[::-1]
            print("\n================== Global Feature Importances ==================")
            for rank, idx in enumerate(ranked_indices, 1):
                print(f"{rank:02d}. {feature_names[idx]:<20} : {importances[idx]:.4f} ({importances[idx]*100:.1f}%)")
            print("="*65)
            return {
                "type": "feature_importance",
                "importances": importances,
                "ranked_features": [feature_names[i] for i in ranked_indices]
            }
        return {}


def main():
    parser = argparse.ArgumentParser(description="Explain GAMA LULC Model")
    parser.add_argument("--data", type=str, default="data/XAI_TRAINING_DATASET.csv")
    args = parser.parse_args()

    default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "XAI_TRAINING_DATASET.csv")
    csv_path = args.data if os.path.exists(args.data) else default_path

    X_train, X_test, y_train, y_test, features = load_and_preprocess_dataset(csv_path)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    explain_tree_model(model, X_test, features)


if __name__ == "__main__":
    main()
