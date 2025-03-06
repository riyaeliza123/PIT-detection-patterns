# PIT tag detection patterns
## Prepare data

The queries for each dataset is saved in [data/queries.md](https://github.com/riyaeliza123/PIT-detection-patterns/blob/main/data/queries.md).
### Data descriptions:

1. loc_code_detection_patterns.csv: This is primary data source. It has summaries about each detection event of a PIT tag. You will find mutliple rows for each tag and each row is a summary of the tag's action when it was detected at that location. It contains the following tag_id, loc_code, start_date, end_date, dwell_time (end datetime -  start datetime),number_of_detections (at that location, during the dwell time). Dwell time can be understood as the time spent by a tag at that location (without moving to the next location).
2. antenna_detection_patterns.csv: Same as above, but an extra column is added - antenna. This dataset is to further explore the movement of a tag. Each location code has multiple antennae.
3. location_lat_long.csv: Latitude and longitude of each location ode and antenna (can be used for vizualization).
4. most_detected_tags.csv: Returns tag_id, number of detections (total) and if the tag was ever found on a cleaning table (yes/no). It is a priliminary dataset to look at tags with unsually large detection counts and investigate.
5. tag summaries.csv and unusual movements.csv: Results from pit_profiles.ipynb

## Analysis : pit_profiles.ipynb
#### 1. Data preperation:
Columns needed:
1. tag_id : The unique PIT tag
2. loc_code : A list of location codes the tag travels through, in the order of travel.
3. number_of_detections : A list containing number of detections at each location, for each event.
4. movement_direction : Using location code, the movement between two locations is classifies as "upstream"/"downstream".
5. time_between_detections : The time difference between detection events are two locations, i.e; the difference the last time it was detected at locaton 1 and the first time if was detected at location 2.

#### 2. Method
Each column has been created in seperate notebooks. movement_direction is from directionality.ipynb and time_between_detections from time_between_detections.ipynb. These results are called into pit_profiles.ipynb to create the final summary.
##### 1. directionality.ipynb:

- Use tag_id and location code from data/loc_code_detection_patterns.csv, group by the tag_id and create a df (sequence_df) where each row is a unique tag, and the two columns are tag id and list of all location codes that the tag has travelled through. 
- Define rules for what upstream and downstream mean. Save them in a dictionary format.
- Now create a new column "movement_direction" that looks at loc_code and labels each movement as upstream or downstream. This will be saved as a list into the same df (sequence_df).
  
##### 2. time_between_detections.ipynb

- Use tag_id, location code, start datetime, end datetime and number of detections from data/loc_code_detection_patterns.csv.
- To calculate the time difference between locations, create a new column, start_shift that shifts the start column up by one row. This makes it convienient to subtract the end time of the current event from the next event's start time.
- The difference will be saved in a new column called time_between_detections.

##### 3. pit_profiles.ipynb

- Pull the resulting dfs from the first two notebooks. Join based on tag_id.
- Save this df as a CSV file (tag summaries.csv).



## Archived analysis
### 1. Sankey diagram (plotly)
For visualization, Sankey menthod was investigated. This does give an overall understanding of movement but fails to provide directionality. This is what an example map looks like: 

<img width="500" alt="image" src="https://github.com/user-attachments/assets/3fa7554c-467c-4990-ac27-26ae74253b8a" />


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