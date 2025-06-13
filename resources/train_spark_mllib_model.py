import pandas as pd
import bz2
import json
import sys
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def main():
    if len(sys.argv) < 2:
        raise ValueError("Debes proporcionar la ruta al archivo JSON comprimido.")

    json_path = sys.argv[1]
    print(f"🟢 Usando archivo JSON: {json_path}")

    with bz2.open(json_path, "rt") as f:
        data = [json.loads(line) for line in f]
    df = pd.DataFrame(data)

    print(f"✅ Datos cargados. Filas: {len(df)}")
    print(f"🔍 Columnas: {df.columns.tolist()}")

    target_column = "ArrDelay"
    if target_column not in df.columns:
        raise ValueError(f"La columna objetivo '{target_column}' no está en los datos.")
    
    y = df[target_column]
    X = df.drop(columns=[target_column])

    # Convertir variables categóricas a dummies
    X = pd.get_dummies(X, drop_first=True)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with mlflow.start_run():
        model = RandomForestRegressor()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)

        print(f"✅ MSE: {mse}")
        mlflow.log_metric("mse", mse)
        mlflow.sklearn.log_model(model, "random_forest_regressor")

if __name__ == "__main__":
    main()

