-- Uber Supply-Demand Gap Analysis - SQL Queries (SQLite)
-- Table: uber_trips

-- --------------------------------------------------------------------
-- Query 1: Overall ride status breakdown
-- Shows how many requests were completed, cancelled, or had no car.
-- --------------------------------------------------------------------
SELECT 
    status,
    COUNT(request_id) AS total_requests,
    ROUND(COUNT(request_id) * 100.0 / (SELECT COUNT(*) FROM uber_trips), 2) AS pct_of_total
FROM uber_trips
GROUP BY status
ORDER BY total_requests DESC;


-- --------------------------------------------------------------------
-- Query 2: Overall completion, cancellation, and car-shortage rates
-- Shows the percentage of all 6,745 requests that were completed vs unfulfilled.
-- --------------------------------------------------------------------
SELECT 
    COUNT(request_id) AS total_demand,
    SUM(CASE WHEN status = 'Trip Completed' THEN 1 ELSE 0 END) AS completed_trips,
    SUM(CASE WHEN status != 'Trip Completed' THEN 1 ELSE 0 END) AS unfulfilled_requests,
    ROUND(SUM(CASE WHEN status = 'Trip Completed' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS completion_rate,
    ROUND(SUM(CASE WHEN status = 'Cancelled' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate,
    ROUND(SUM(CASE WHEN status = 'No Cars Available' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS no_cars_rate,
    ROUND(SUM(CASE WHEN status != 'Trip Completed' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS unfulfilled_rate
FROM uber_trips;


-- --------------------------------------------------------------------
-- Query 3: Status breakdown by pickup location (City vs. Airport)
-- Compares request volumes, cancellations, and shortages between locations.
-- --------------------------------------------------------------------
SELECT 
    pickup_point,
    COUNT(request_id) AS total_requests,
    SUM(CASE WHEN status = 'Trip Completed' THEN 1 ELSE 0 END) AS completed_trips,
    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_trips,
    SUM(CASE WHEN status = 'No Cars Available' THEN 1 ELSE 0 END) AS no_cars_available,
    ROUND(SUM(CASE WHEN status = 'Trip Completed' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS completion_rate,
    ROUND(SUM(CASE WHEN status = 'Cancelled' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate,
    ROUND(SUM(CASE WHEN status = 'No Cars Available' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS no_cars_rate,
    ROUND(SUM(CASE WHEN status != 'Trip Completed' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS unfulfilled_rate
FROM uber_trips
GROUP BY pickup_point
ORDER BY total_requests DESC;


-- --------------------------------------------------------------------
-- Query 4: Total demand and completed supply by hour
-- Tracks request volume and unfulfilled trips across the 24 hours of the day.
-- --------------------------------------------------------------------
SELECT 
    request_hour,
    COUNT(request_id) AS total_demand,
    SUM(CASE WHEN status = 'Trip Completed' THEN 1 ELSE 0 END) AS supply_completed,
    SUM(CASE WHEN status != 'Trip Completed' THEN 1 ELSE 0 END) AS gap_unfulfilled,
    ROUND(SUM(CASE WHEN status != 'Trip Completed' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS gap_rate_pct
FROM uber_trips
GROUP BY request_hour
ORDER BY request_hour ASC;


-- --------------------------------------------------------------------
-- Query 5: Top 5 hours with the most unfulfilled requests
-- Focuses on total failure volume rather than percentage alone.
-- --------------------------------------------------------------------
SELECT 
    request_hour,
    COUNT(request_id) AS total_requests,
    SUM(CASE WHEN status != 'Trip Completed' THEN 1 ELSE 0 END) AS unfulfilled_count,
    ROUND(SUM(CASE WHEN status != 'Trip Completed' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS unfulfilled_rate_pct,
    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancellations,
    SUM(CASE WHEN status = 'No Cars Available' THEN 1 ELSE 0 END) AS no_cars_count
FROM uber_trips
GROUP BY request_hour
ORDER BY unfulfilled_count DESC
LIMIT 5;


-- --------------------------------------------------------------------
-- Query 6: Morning rush cancellations in the City (5:00 AM to 9:59 AM)
-- Evaluates City cancellations during the 5 peak morning commute hours.
-- --------------------------------------------------------------------
SELECT 
    request_hour,
    COUNT(request_id) AS city_requests,
    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancellations,
    SUM(CASE WHEN status = 'Trip Completed' THEN 1 ELSE 0 END) AS completed_trips,
    ROUND(SUM(CASE WHEN status = 'Cancelled' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct
FROM uber_trips
WHERE pickup_point = 'City' 
  AND request_hour BETWEEN 5 AND 9
GROUP BY request_hour
ORDER BY request_hour ASC;


-- --------------------------------------------------------------------
-- Query 7: Evening rush car shortages at the Airport (5:00 PM to 9:59 PM)
-- Evaluates car unavailability during the 5 peak evening return hours.
-- --------------------------------------------------------------------
SELECT 
    request_hour,
    COUNT(request_id) AS airport_requests,
    SUM(CASE WHEN status = 'No Cars Available' THEN 1 ELSE 0 END) AS no_cars_count,
    SUM(CASE WHEN status = 'Trip Completed' THEN 1 ELSE 0 END) AS completed_trips,
    ROUND(SUM(CASE WHEN status = 'No Cars Available' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS no_cars_rate_pct
FROM uber_trips
WHERE pickup_point = 'Airport' 
  AND request_hour BETWEEN 17 AND 21
GROUP BY request_hour
ORDER BY request_hour ASC;


-- --------------------------------------------------------------------
-- Query 8: Ranking problem hours and locations using a window function
-- Ranks location and hour combinations by total unfulfilled requests.
-- --------------------------------------------------------------------
WITH LocationHourlyStats AS (
    SELECT 
        pickup_point,
        request_hour,
        COUNT(request_id) AS total_requests,
        SUM(CASE WHEN status != 'Trip Completed' THEN 1 ELSE 0 END) AS unfulfilled_count,
        SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancellations,
        SUM(CASE WHEN status = 'No Cars Available' THEN 1 ELSE 0 END) AS no_cars_count,
        ROUND(SUM(CASE WHEN status != 'Trip Completed' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 2) AS unfulfilled_rate_pct
    FROM uber_trips
    GROUP BY pickup_point, request_hour
)
SELECT 
    RANK() OVER (ORDER BY unfulfilled_count DESC) AS severity_rank,
    pickup_point,
    request_hour,
    total_requests,
    unfulfilled_count,
    unfulfilled_rate_pct,
    cancellations,
    no_cars_count,
    CASE 
        WHEN cancellations > no_cars_count THEN 'Driver Cancellations'
        ELSE 'Car Shortage (No Cars)'
    END AS dominant_issue
FROM LocationHourlyStats
ORDER BY severity_rank ASC
LIMIT 10;
