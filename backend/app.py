from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import json
import os

app = Flask(__name__)
CORS(app)

# -----------------------------------------------------------------------------
# LOAD MODEL ARTIFACTS (TREE MODEL – NO SCALER)
# -----------------------------------------------------------------------------
try:
    model = joblib.load("career_prediction_model.joblib")
    label_encoder = joblib.load("label_encoder.joblib")

    with open("feature_order.json", "r") as f:
        FEATURE_ORDER = json.load(f)["feature_order"]

    print("✅ Model loaded successfully")
    print(f"✅ Expected feature count: {len(FEATURE_ORDER)}")

except Exception as e:
    print("❌ Error loading model artifacts:", e)
    model = None
    FEATURE_ORDER = []

# -----------------------------------------------------------------------------

# HOME ROUTE
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to AI Career Guidance System",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "careers": "/careers",
            "predict": "/predict (POST)"
        }
    }), 200
# HEALTH CHECK
# -----------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "OK",
        "model_loaded": model is not None,
        "features_expected": len(FEATURE_ORDER)
    }), 200

# -----------------------------------------------------------------------------
# PREDICTION ENDPOINT
# -----------------------------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        data = request.get_json()

        # -------------------------------------------------
        # 1. APTITUDE FEATURES (8) — RANGE: 0–20
        # -------------------------------------------------
        apt = data.get("aptitudes", {})

        aptitude_values = [
            float(apt.get("linguistic", 10)),
            float(apt.get("musical", 10)),
            float(apt.get("bodily", 10)),
            float(apt.get("logical_mathematical", 10)),
            float(apt.get("spatial_visualization", 10)),
            float(apt.get("interpersonal", 10)),
            float(apt.get("intrapersonal", 10)),
            float(apt.get("naturalist", 10)),
        ]

        aptitude_array = np.array(aptitude_values)

        # -------------------------------------------------
        # 2. PERFORMANCE FEATURES (8) — POOR/AVG/BEST
        # -------------------------------------------------
        perf = data.get("performance", {})
        perf_map = {"POOR": 0, "AVG": 1, "BEST": 2}

        performance_values = [
            perf_map.get(perf.get("project_performance", "AVG"), 1),
            perf_map.get(perf.get("practical_skills", "AVG"), 1),
            perf_map.get(perf.get("research_interest", "AVG"), 1),
            perf_map.get(perf.get("communication_skills", "AVG"), 1),
            perf_map.get(perf.get("leadership_qualities", "AVG"), 1),
            perf_map.get(perf.get("teamwork", "AVG"), 1),
            perf_map.get(perf.get("time_management", "AVG"), 1),
            perf_map.get(perf.get("self_learning", "AVG"), 1),
        ]

        performance_array = np.array(performance_values)

        # -------------------------------------------------
        # 3. FEATURE ENGINEERING (100% MATCH TRAINING)
        # -------------------------------------------------
        total_aptitude = aptitude_array.sum()
        aptitude_diversity = aptitude_array.std()

        intelligence_index = (aptitude_array[3] + aptitude_array[4]) / 2
        creativity_index = (
            aptitude_array[0] +
            aptitude_array[1] +
            aptitude_array[2] +
            aptitude_array[5]
        ) / 4

        physical_index = aptitude_array[2]
        social_index = (aptitude_array[5] + aptitude_array[6]) / 2

        performance_score = performance_array.mean()

        # SAME threshold as training (≈ 1.12)
        is_high_performer = 1 if performance_score >= 1.12 else 0

        # Cluster optional (frontend can send later)
        cluster = int(data.get("cluster", 0))

        # -------------------------------------------------
        # 4. FINAL FEATURE VECTOR (25 FEATURES)
        # -------------------------------------------------
        feature_vector = (
            aptitude_values +
            performance_values +
            [
                total_aptitude,
                aptitude_diversity,
                intelligence_index,
                creativity_index,
                physical_index,
                social_index,
                performance_score,
                is_high_performer,
                cluster
            ]
        )

        if len(feature_vector) != len(FEATURE_ORDER):
            return jsonify({
                "error": "Feature count mismatch",
                "expected": len(FEATURE_ORDER),
                "received": len(feature_vector)
            }), 400

        X = np.array(feature_vector).reshape(1, -1)

        # -------------------------------------------------
        # 5. TOP-5 PREDICTIONS
        # -------------------------------------------------
        probs = model.predict_proba(X)[0]
        top_idx = np.argsort(probs)[-5:][::-1]

        results = []
        for i, idx in enumerate(top_idx):
            results.append({
                "rank": i + 1,
                "career": label_encoder.classes_[idx],
                "confidence": round(float(probs[idx] * 100), 2)
            })

        return jsonify({
            "status": "success",
            "top_predictions": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# CAREERS LIST (ALL 72 CAREERS)
# -----------------------------------------------------------------------------
@app.route("/careers", methods=["GET"])
def careers():
    return jsonify({
        "total": len(label_encoder.classes_),
        "careers": label_encoder.classes_.tolist()
    }), 200

# -----------------------------------------------------------------------------
# RUN SERVER
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
