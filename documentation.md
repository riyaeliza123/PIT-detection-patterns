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
The queries for each dataset is saved in data/queries.md

## Analysis
#### 1. Data preperation:

#### 2. Method




## Archived analysis
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