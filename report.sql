WITH trip_durations AS (
    SELECT
        r.id AS ride_id,
        r.driver_id,
        MIN(CASE WHEN re.description = 'Driver arrived at pickup location' THEN re.created_at END) AS pickup_time,
        MIN(CASE WHEN re.description = 'Ride completed' THEN re.created_at END) AS dropoff_time
    FROM ride r
    INNER JOIN ride_event re ON r.id = re.ride_id
    WHERE re.description IN ('Driver arrived at pickup location', 'Ride completed')
    GROUP BY r.id, r.driver_id
    HAVING
        MIN(CASE WHEN re.description = 'Driver arrived at pickup location' THEN re.created_at END) IS NOT NULL
        AND MIN(CASE WHEN re.description = 'Ride completed' THEN re.created_at END) IS NOT NULL
        AND EXTRACT(EPOCH FROM (
            MIN(CASE WHEN re.description = 'Ride completed' THEN re.created_at END) -
            MIN(CASE WHEN re.description = 'Driver arrived at pickup location' THEN re.created_at END)
        )) / 3600 > 1
)
SELECT
    TO_CHAR(td.pickup_time, 'YYYY-MM') AS "Month",
    u.first_name || ' ' || LEFT(u.last_name, 1) AS "Driver",
    COUNT(*) AS "Count of Trips > 1 hr"
FROM trip_durations td
INNER JOIN "user" u ON td.driver_id = u.id
GROUP BY TO_CHAR(td.pickup_time, 'YYYY-MM'), u.first_name, u.last_name
ORDER BY "Month", "Driver";