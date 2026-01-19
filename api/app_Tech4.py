from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os
from datetime import datetime
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.impute import SimpleImputer
from utils import FeatureEngineeringTransformer 

app = Flask(__name__)

# Caminhos
HISTORICO_FILE = os.path.join("Dados", "Dados Históricos - Ibovespa_ate_09_01.csv")
MODEL_FILE = os.path.join("modelo", "modelo_classificador_knn.joblib")
LOG_FILE = os.path.join("logs", "consultas.csv")

# Garantir que pasta de logs existe
os.makedirs("logs", exist_ok=True)
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["ID", "DataConsulta", "Ultimo", "Abertura", "Maxima", "Minima", "Previsao"]).to_csv(LOG_FILE, index=False)

# Carregar modelo e transformer
obj = joblib.load(MODEL_FILE)
feature_eng_treino = obj["transformer"]   # usado para métricas
modelo = obj["modelo"]

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        df_input = pd.DataFrame([data])

        # Normalizar nomes
        df_input = df_input.rename(columns={
            "Último": "Ultimo",
            "Máxima": "Maxima",
            "Mínima": "Minima"
        })

        # Usar transformer em modo previsão 
        feature_eng_prev = FeatureEngineeringTransformer(modo="previsao")
        X_input = feature_eng_prev.transform(df_input).drop(columns=["Target","Data","Vol.","Var%"], errors="ignore")

        # Substituir NaN por 0
        imputer = SimpleImputer(strategy="constant", fill_value=0)
        X_input = imputer.fit_transform(X_input)

        # Previsão
        prediction = modelo.predict(X_input)[0]

        # Registrar no log
        df_log = pd.read_csv(LOG_FILE)
        novo_id = len(df_log) + 1
        df_log = pd.concat([df_log, pd.DataFrame([{
            "ID": novo_id,
            "DataConsulta": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Ultimo": data.get("Ultimo"),
            "Abertura": data.get("Abertura"),
            "Maxima": data.get("Maxima"),
            "Minima": data.get("Minima"),
            "Previsao": int(prediction)
        }])], ignore_index=True)
        df_log.to_csv(LOG_FILE, index=False)

        return jsonify({"prediction": int(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/metrics", methods=["GET"])
def metrics():
    try:
        df = pd.read_csv(HISTORICO_FILE)
        df = df.rename(columns={
            "Último": "Ultimo",
            "Máxima": "Maxima",
            "Mínima": "Minima"
        })

        # Aplicar transformer em modo treino 
        df_transformed = feature_eng_treino.transform(df)

        y_true = df_transformed["Target"]
        X = df_transformed.drop(columns=["Target","Data","Vol.","Var%"], errors="ignore")

        y_pred = modelo.predict(X)

        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)

        return jsonify({
            "accuracy": acc,
            "f1": f1,
            "precision": precision,
            "recall": recall
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
