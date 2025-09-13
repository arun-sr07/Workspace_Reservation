# ml/recommendation_service.py
import joblib
import pandas as pd
import pymysql
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "seat_recommender.pkl")

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("⚠️ ML model not found. Please run train_model.py first.")
    return joblib.load(MODEL_PATH)

def get_connection():
    """Return a pymysql connection object."""
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",  # 🔑 update this
        database="workspace_reservation",
        cursorclass=pymysql.cursors.DictCursor
    )

def get_user_seat_history(user_id):
    """Fetch historical reservation data for the given user."""
    conn = get_connection()
    query = """
    SELECT seat_id, resource_id, DAYNAME(reservation_date) AS day_of_week,
           DATEDIFF(reservation_date, 
                    LAG(reservation_date) OVER (PARTITION BY user_id, seat_id ORDER BY reservation_date)) AS last_reserved_gap
    FROM reservations
    WHERE user_id = %s
    """
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()

    df['last_reserved_gap'] = df['last_reserved_gap'].fillna(-1)
    return df

def get_recommended_seats(user_id, resource_id, reservation_date):
    """Return top 3 recommended seats with predicted probability."""
    model = load_model()
    history_df = get_user_seat_history(user_id)

    if history_df.empty:
        return []  # No past data, no recommendations

    # Prepare candidates (unique seat_ids for this resource)
    unique_seats = history_df[history_df['resource_id'] == resource_id]['seat_id'].unique()

    if len(unique_seats) == 0:
        return []  # No history for this resource

    # Build prediction dataframe
    pred_df = pd.DataFrame({
        "seat_id": unique_seats,
        "resource_id": [resource_id] * len(unique_seats),
        "day_of_week": [reservation_date.strftime("%A")] * len(unique_seats),
        "last_reserved_gap": [-1] * len(unique_seats)
    })

    # Predict probabilities
    probabilities = model.predict_proba(pred_df)[:, 1]  # class 1 = reserved again
    pred_df['probability'] = probabilities

    # Sort by probability and return top 3
    pred_df = pred_df.sort_values(by="probability", ascending=False).head(3)
    return list(zip(pred_df['seat_id'], pred_df['probability']))
