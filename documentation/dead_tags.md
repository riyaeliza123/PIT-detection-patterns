Dead tags: Tags that are present at the same locaton for extended period of time

```
WITH detection_counts AS (
  SELECT tag_id, count(*), 
    o.tag_date, o.earliest_detection_date, o.latest_detection_date, o.latest_detection_date - o.earliest_detection_date as detection_duration_days, 
    (o.latest_detection_date - o.earliest_detection_date)/count(*)::NUMERIC as detection_rate,
    CASE 
        WHEN ct.tag_id_long IS NOT NULL THEN 'yes'
        ELSE 'no'
    END AS in_cleaning_table
  FROM detections d
  LEFT JOIN outmigrant_return o
  ON tag_id = o.tag_id_long
  LEFT JOIN cleaning_table ct
  ON d.tag_id = ct.tag_id_long
  WHERE tag_id IN (SELECT DISTINCT tag_id_long FROM outmigrant_return WHERE return = 1) 
  GROUP BY d.tag_id, ct.tag_id_long, o.tag_date, o.earliest_detection_date, o.latest_detection_date
  ORDER BY detection_rate, count(*) DESC
)

SELECT * 
FROM detection_counts
WHERE detection_duration_days > 0 and count > 1500
```

Note: ```count > 1500``` can be altered (it is an assumed cut-off). 

Check for tags with unusually large number of detections. We cannot naively conclude that large number of detections = dead tag because these detections could be over a long period. It is important to consider the time period over which these detections are recorded. And so, a detection rate will be helful. Detecion rate is time period divided by the number of detections.

In this query, the smaller the detection_rate, the more likely it is a dead tag, meaning in a small duration we see a lot of detections. Using detection_rate we can create a cut-off for what is likely a dead tag and what is not.

Insights:
1. When the cut-off is "detection_duration_days > 0 and count > 1500", these are    definitly all dead tags. They were all at the same location for that given time. Here the maximum detection_rate = 0.06.
2. When the cut-off is "detection_duration_days > 0" when inspecting tags with a few hundred detections and a low detection_rate, there is a pattern where over a few days days it is stuck at one place, gets washed down and is stuck at the next location. (eg: 989.002028405138)
