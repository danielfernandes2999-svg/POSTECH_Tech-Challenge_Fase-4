import pandas as pd
import joblib
from sklearn.neighbors import KNeighborsClassifier
from utils import FeatureEngineeringTransformer

DATA_FILE = "Dados/Dados Históricos - Ibovespa_ate_09_01.csv"
MODEL_FILE = "modelo/modelo_classificador_knn.joblib"

# Carregar dados
df = pd.read_csv(DATA_FILE)

# Normalizar nomes
df = df.rename(columns={
    "Último": "Ultimo",
    "Máxima": "Maxima",
    "Mínima": "Minima"
})

# Aplicar engenharia de features
feature_eng = FeatureEngineeringTransformer()
df_transformed = feature_eng.transform(df)

# Separar X e y
X = df_transformed.drop(columns=["Target", "Data", "Vol.", "Var%"], errors="ignore")
y = df_transformed["Target"]

# Treinar modelo direto (sem pipeline)
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X, y)

# Salvar modelo + transformer juntos em um dicionário
joblib.dump({"transformer": feature_eng, "modelo": knn}, MODEL_FILE)
print(f"✅ Modelo KNN salvo em {MODEL_FILE}")
