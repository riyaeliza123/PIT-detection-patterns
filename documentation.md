# PIT tag detection patterns

First , identify the tags with most detections. Start by observing patterns in these tags:
```
SELECT tag_id, count(*), 
  CASE 
      WHEN ct.tag_id_long IS NOT NULL THEN 'yes'
      ELSE 'no'
  END AS in_cleaning_table
FROM detections d
LEFT JOIN cleaning_table ct
ON d.tag_id = ct.tag_id_long
GROUP BY d.tag_id, ct.tag_id_long
ORDER BY count(*) DESC
```


Dwell time at each antenna (and number of continuous detections) can be helpful to understand what type of animal (fish or other) is holding the PIT tag:
1. Overview of movement using loc_code:
```
WITH individual_tag_detected AS(
  SELECT datetime, detection_date, detection_time, tag_id, loc_code 
  FROM detections
  WHERE  tag_id = '989.001038869060'
  ORDER BY datetime 
),
ranked_data AS (
    SELECT datetime, detection_date, detection_time, loc_code, ROW_NUMBER() OVER (ORDER BY datetime) AS row_id
    FROM individual_tag_detected
),
grouped_data AS (
    SELECT 
        loc_code,
        datetime,
        detection_date,
        detection_time,
        row_id,
        LAG(loc_code) OVER (ORDER BY row_id) AS prev_loc_code,
        CASE 
            WHEN LAG(loc_code) OVER (ORDER BY row_id) IS DISTINCT FROM loc_code THEN row_id
        END AS group_start
    FROM ranked_data
),
group_ids AS (
    SELECT 
        *,
        MAX(group_start) OVER (ORDER BY row_id) AS group_id
    FROM grouped_data
),
aggregated_data AS (
    SELECT 
        loc_code,
        MIN(detection_date) AS start_date,
        MIN(datetime) AS start_time,
        MAX(detection_date) AS end_date,
        MAX(datetime) AS end_time,
        count(*) as number_of_detections
    FROM group_ids
    GROUP BY loc_code, group_id
)
SELECT 
    loc_code,
    start_date,
    end_date,
    end_time - start_time as dwell_time,
    number_of_detections
FROM aggregated_data
ORDER BY start_date, start_time
```

2. Inspect further by analysing antenna at each loc_code:
```
WITH individual_tag_detected AS (
    SELECT datetime, detection_date, detection_time, tag_id, loc_code, antenna
    FROM detections
    WHERE tag_id = '989.001038869060'
    ORDER BY datetime
),
ranked_data AS (
    SELECT datetime, detection_date, detection_time, loc_code, antenna,
           ROW_NUMBER() OVER (ORDER BY datetime) AS row_id
    FROM individual_tag_detected
),
grouped_data AS (
    SELECT
        loc_code,
        antenna,
        datetime,
        detection_date,
        detection_time,
        row_id,
        LAG(loc_code) OVER (ORDER BY row_id) AS prev_loc_code,
        LAG(antenna) OVER (ORDER BY row_id) AS prev_antenna,
        CASE
            WHEN LAG(loc_code) OVER (ORDER BY row_id) IS DISTINCT FROM loc_code
                 OR LAG(antenna) OVER (ORDER BY row_id) IS DISTINCT FROM antenna THEN row_id
        END AS group_start
    FROM ranked_data
),
group_ids AS (
    SELECT
        *,
        MAX(group_start) OVER (ORDER BY row_id) AS group_id
    FROM grouped_data
),
aggregated_data AS (
    SELECT
        loc_code,
        antenna,
        MIN(detection_date) AS start_date,
        MIN(datetime) AS start_time,
        MAX(detection_date) AS end_date,
        MAX(datetime) AS end_time,
        COUNT(*) AS number_of_detections
    FROM group_ids
    GROUP BY loc_code, antenna, group_id
)
SELECT
    loc_code,
    antenna,
    start_date,
    end_date,
    end_time - start_time AS dwell_time,
    number_of_detections
FROM aggregated_data
ORDER BY start_date, start_time
```

For visualization, Sankey menthod was investigated. This does give an over all understanding of movement but fails to provide directionality. The code notebook has been archived.