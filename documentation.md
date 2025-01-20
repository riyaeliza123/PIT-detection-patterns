# PIT tag detection patterns
## Prepare data
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
  SELECT tag_id, datetime, detection_date, detection_time, loc_code 
  FROM detections
--  WHERE  tag_id = '989.001038869060'
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

2. Inspect further by analysing antenna at each loc_code:
```
WITH individual_tag_detected AS (
    SELECT datetime, detection_date, detection_time, tag_id, loc_code, antenna
    FROM detections
    -- WHERE tag_id = '989.001038869060'
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
## Methods of analysis
### 1. Sankey diagram (plotly)
For visualization, Sankey menthod was investigated. This does give an overall understanding of movement but fails to provide directionality. This is what an example map looks like: 

<img width="703" alt="image" src="https://github.com/user-attachments/assets/3fa7554c-467c-4990-ac27-26ae74253b8a" />


The sankey diagram for tag_id = "989.001038869060" looks like this:

<img width="699" alt="image" src="https://github.com/user-attachments/assets/d98e7bc7-5a19-445d-83f5-593e8f5a2c55" />

Multiple issues at first glance: the nodes are not representative of the way antennas are located and again direction cannot be determined. Perhaps a similar approach on a geographic map will be better. This code can be found in the "archived methods" folder.

### 2. Unsupervised learning to create profiles
#### 1. Data preperation:

The columns needed are:
1. tag_id
2. subloc (upstream/downstream)
3. Number of detections (per location, per event)
4. Dwell time (during each detection event)

#### 2. Method:

1. Feature engineering - subloc into one-hot encoding
2. Create a df where the columns are tag_id, subloc_sequence (a list showing the direction of the tag), detection_counts (list of all detection events), dwell_timings(list of all dwell times per detection event).



