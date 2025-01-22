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

### 2. Similarity scores to create profiles
#### 1. Data preperation:

The columns needed are:
1. tag_id
2. subloc (upstream/downstream)
3. Number of detections (per location, per event)
4. Dwell time (during each detection event)

The dataset (data/sequence_df.csv) reads like this (the 3rd row for example): "The tag 989.001006608003 has been detected downstream, downsteam (different location) and then upstream. It was detected 40 times at the first location, then 4 times at the second location and again 4 times at the final upstream location. The tag spent 1043247.56 seconds (12 days) at the first downstream location and effectively not much time at the other two locations. 0 seconds mean that the tag moved around and did not really "dwell" at that area."

#### 2. Method:

1. Feature engineering - subloc into one-hot encoding
2. Create a df where the columns are tag_id, subloc_sequence (a list showing the direction of the tag), detection_counts (list of all detection events), dwell_timings(list of all dwell times per detection event).
3. Remove all cells with Nan values
4. The goal is to create similarity scores of sorts. The magnitude of the score should be able to tell us about the relative movement of the tag. This would need multiplication/product operations. We have 0s in our dataset that holds meaning (in subloc it means upsteam and in dwell_times it means that the tag did not spend much time there). Multiplication could mean that we lose those factors. So, replace 0 with a near 0 value like a negative exponent of 1 (0.01 for example), so that we can keep the essence of the value and not lose the factor.
5. Similarity score is calculated by dividing the dwell time with th detection count. This gives us the time for each detection(on average) in seconds. Then multiply these values with 0 or 0.01 (downstream/upsteam) based on the subloc_sequence column and sum them to get our "similarity scores".
6. Sorting the dataframe based on the score helps identify profiles or groups that show similar behaviour. Since the scores are inflated and exist in 10,000 - 100,000 range, create a new column by dividing this value by 86400 to convert them into smaller vales. What this does is essencially convert seconds into days, thus smaller values.



