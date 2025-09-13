import pandas as pd
import pymysql
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier

def train_seat_model():
    # ✅ Use pymysql (since you are using it everywhere)
    conn = pymysql.connect(
        host="localhost", user="root", password="root", database="workspace_reservation"
    )

    df = pd.read_sql("SELECT * FROM user_seat_training_data", conn)
    conn.close()

    if df.empty:
        print("⚠️ No reservation data found. Model not trained.")
        return

    # ✅ Ensure numeric columns are numeric
    numeric_cols = ['seat_id', 'resource_id', 'day_of_week', 'last_reserved_gap']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df['last_reserved_gap'] = df['last_reserved_gap'].fillna(-1)

    X = df[numeric_cols]
    y = df['reserved_again'].astype(int)  # make sure target is int

    # ✅ ColumnTransformer expects categorical columns as string
    X['day_of_week'] = X['day_of_week'].astype(str)

    preprocessor = ColumnTransformer(
        transformers=[
            ('day_of_week', OneHotEncoder(handle_unknown='ignore'), ['day_of_week'])
        ],
        remainder='passthrough'
    )

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    model.fit(X, y)
    joblib.dump(model, "ml/seat_recommender.pkl")
    print("✅ Model trained and saved to ml/seat_recommender.pkl")

if __name__ == "__main__":
    train_seat_model()
