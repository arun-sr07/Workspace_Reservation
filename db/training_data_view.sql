-- db/training_data_view.sql
USE workspace_reservation;

CREATE OR REPLACE VIEW user_seat_training_data AS
SELECT 
    r.user_id,
    r.seat_id,
    r.resource_id,
    DAYNAME(r.reservation_date) AS day_of_week,
    DATEDIFF(
        r.reservation_date,
        LAG(r.reservation_date) OVER (PARTITION BY r.user_id, r.seat_id ORDER BY r.reservation_date)
    ) AS last_reserved_gap,
    CASE 
        WHEN LEAD(r.reservation_date) OVER (PARTITION BY r.user_id, r.seat_id ORDER BY r.reservation_date)
             IS NOT NULL THEN 1
        ELSE 0
    END AS reserved_again
FROM reservations r
WHERE r.seat_id IS NOT NULL;
