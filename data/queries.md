1. antenna_detection_patterns.csv
```
-- Generalized for all tags, can filter by tag ID
WITH individual_tag_detected AS (
    SELECT datetime, detection_date, detection_time, tag_id, loc_code, antenna
    FROM detections
    WHERE tag_id IN (SELECT DISTINCT tag_id_long FROM outmigrant_return WHERE return = 1) and detection_date > DATE '2017-01-01' -- returns only and date being 2012 is a recording error
    ORDER BY datetime
),
ranked_data AS (
    SELECT tag_id, datetime, detection_date, detection_time, loc_code, antenna,
           ROW_NUMBER() OVER (ORDER BY datetime) AS row_id
    FROM individual_tag_detected
),
grouped_data AS (
    SELECT
        tag_id,
        loc_code,
        antenna,
        datetime,
        detection_date,
        detection_time,
        row_id,
        LAG(loc_code) OVER (PARTITION BY tag_id ORDER BY row_id) AS prev_loc_code,
        LAG(antenna) OVER (PARTITION BY tag_id ORDER BY row_id) AS prev_antenna,
        CASE
            WHEN LAG(loc_code) OVER (PARTITION BY tag_id ORDER BY row_id) IS DISTINCT FROM loc_code
                 OR LAG(antenna) OVER (PARTITION BY tag_id ORDER BY row_id) IS DISTINCT FROM antenna THEN row_id
        END AS group_start
    FROM ranked_data
),
group_ids AS (
    SELECT
        *,
        MAX(group_start) OVER (PARTITION BY tag_id ORDER BY row_id) AS group_id
    FROM grouped_data
),
aggregated_data AS (
    SELECT
        tag_id,
        loc_code,
        antenna,
        MIN(detection_date) AS start_date,
        MIN(datetime) AS start_time,
        MAX(detection_date) AS end_date,
        MAX(datetime) AS end_time,
        COUNT(*) AS number_of_detections
    FROM group_ids
    GROUP BY loc_code, antenna, group_id, tag_id
)
SELECT
    tag_id,
    loc_code,
    antenna,
    start_date,
    end_date,
    end_time - start_time AS dwell_time,
    number_of_detections
FROM aggregated_data
-- WHERE tag_id = '989.001006676104'
ORDER BY start_date, start_time
```

2. loc_code_detection_patterns.csv
```
WITH individual_tag_detected AS(
  SELECT tag_id, datetime, detection_date, detection_time, loc_code 
  FROM detections
  WHERE tag_id IN (SELECT DISTINCT tag_id_long FROM outmigrant_return WHERE return = 1) and detection_date > DATE '2017-01-01' -- returns only and date being 2012 is a recording error
  ORDER BY datetime 
),
ranked_data AS (
    SELECT tag_id, datetime, detection_date, detection_time, loc_code, ROW_NUMBER() OVER (ORDER BY datetime) AS row_id
    FROM individual_tag_detected
),
grouped_data AS (
    SELECT 
        tag_id,
        loc_code,
        datetime,
        detection_date,
        detection_time,
        row_id,
        LAG(loc_code) OVER (PARTITION BY tag_id ORDER BY row_id) AS prev_loc_code,
        CASE 
            WHEN LAG(loc_code) OVER (PARTITION BY tag_id ORDER BY row_id) IS DISTINCT FROM loc_code THEN row_id
        END AS group_start
    FROM ranked_data
),
group_ids AS (
    SELECT 
        *,
        MAX(group_start) OVER (PARTITION BY tag_id ORDER BY row_id) AS group_id
    FROM grouped_data
    -- WHERE tag_id = '989.001038869060'
),
aggregated_data AS (
    SELECT 
        tag_id,
        loc_code,
        MIN(detection_date) AS start_date,
        MIN(datetime) AS start_time,
        MAX(detection_date) AS end_date,
        MAX(datetime) AS end_time,
        count(*) as number_of_detections
    FROM group_ids
    GROUP BY loc_code, group_id, tag_id
)
SELECT 
    tag_id,
    loc_code,
    start_date,
    end_date,
    end_time - start_time as dwell_time,
    number_of_detections
FROM aggregated_data
ORDER BY start_date, start_time
```

3. location_lat_long.csv
```
SELECT DISTINCT d.loc_code, antenna, latitude, longitude, subloc
FROM detections d 
JOIN location l ON d.loc_code = l.loc_code
WHERE tag_id IN (SELECT DISTINCT tag_id_long FROM outmigrant_and_return_materialized WHERE return = 1) 
GROUP BY d.loc_code, antenna, latitude, longitude, subloc
```

4. most_detected_tags.csv
```
SELECT tag_id, count(*), 
  CASE 
      WHEN ct.tag_id_long IS NOT NULL THEN 'yes'
      ELSE 'no'
  END AS in_cleaning_table
FROM detections d
LEFT JOIN cleaning_table ct
ON d.tag_id = ct.tag_id_long
WHERE tag_id IN (SELECT DISTINCT tag_id_long FROM outmigrant_return WHERE return = 1)
GROUP BY d.tag_id, ct.tag_id_long
ORDER BY count(*) DESC

```