# ml/recommendation_service.py
import joblib
import pandas as pd
import pymysql
import os
from collections import Counter
from sqlalchemy import create_engine
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), "seat_recommender.pkl")

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("⚠️ ML model not found. Please run train_model.py first.")
    return joblib.load(MODEL_PATH)

def get_connection():
    """Return a SQLAlchemy engine for pandas compatibility."""
    engine = create_engine("mysql+pymysql://root:root@localhost/workspace_reservation")
    return engine

def get_user_seat_history(user_id):
    engine = get_connection()
    query = """
    SELECT seat_id, resource_id, reservation_date,
           DAYNAME(reservation_date) AS day_of_week,
           DATEDIFF(reservation_date, 
                    LAG(reservation_date) OVER (PARTITION BY user_id, seat_id ORDER BY reservation_date)) AS last_reserved_gap
    FROM reservations
    WHERE user_id = %s
    """
    df = pd.read_sql(query, engine, params=(user_id,))
    

    if df.empty:
        print(f"DEBUG: No history found for user_id={user_id}")
        return df

    # Drop bogus "header row" if present
    if df.iloc[0].tolist() == df.columns.tolist():
        print("⚠️ Detected header row inside data, dropping it...")
        df = df.iloc[1:].reset_index(drop=True)

    # Convert types safely
    df["seat_id"] = pd.to_numeric(df["seat_id"], errors="coerce")
    df["resource_id"] = pd.to_numeric(df["resource_id"], errors="coerce")
    df["last_reserved_gap"] = pd.to_numeric(df["last_reserved_gap"], errors="coerce").fillna(-1)

    return df


def get_recommended_seats(user_id, resource_id, reservation_date):
    model = load_model()
    history_df = get_user_seat_history(user_id)

    if history_df.empty:
        return []

    user_seats = history_df[history_df['resource_id'] == resource_id]['seat_id'].tolist()
    if not user_seats:
        return []

    seat_counts = Counter(user_seats)

    if isinstance(reservation_date, str):
        reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()
    day_of_week = str(reservation_date.isoweekday() % 7 + 1)

    pred_df = pd.DataFrame([{
        "seat_id": seat,
        "resource_id": resource_id,
        "day_of_week": day_of_week,
        "last_reserved_gap": -1
    } for seat in set(user_seats)])

    try:
        probabilities = model.predict_proba(pred_df)[:, 1]
        pred_df['probability'] = probabilities
    except Exception:
        return fallback_top_seats(user_seats)

    if pred_df['probability'].nunique() == 1:
        return fallback_top_seats(user_seats)

    pred_df = pred_df.sort_values(by="probability", ascending=False).head(3)
    # Return with count info
    return [(row['seat_id'], row['probability'], seat_counts[row['seat_id']])
            for _, row in pred_df.iterrows()]


from collections import Counter

def fallback_top_seats(user_seats):
    """Return top seats based on most frequent user reservations."""
    seat_counts = Counter(user_seats)
    total = sum(seat_counts.values())
    top_three = seat_counts.most_common(3)
    # Return tuple: (seat_id, frequency_ratio, count)
    return [(seat, count / total, count) for seat, count in top_three]

