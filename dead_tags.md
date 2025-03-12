Hypothesis for dead tags: Tags that are present at the same locaton for extended period of time

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
WHERE detection_duration_days > 0 and count > 3000
```

Note: ```count > 3000``` can be altered. In this query, the smaller the detection_rate, the more likely it is a dead tag, meaning in a small duration we see a lot of detections.
