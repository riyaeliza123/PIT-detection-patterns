# PIT-detection-patterns
A set of workflows to learn about movement patterns of returning PIT tags and in-turn be able to profile and group those movements.
<br> 
## Notebooks:
1. **tag_summaries.ipynb** : A preliminary notebook to learn about a tag. The user can get information specific to a tag like the first and last date of detection, number of detections and more. It will assist downstream analytics and cross-examination. An [app](https://pit-tag-summaries.streamlit.app/) has been created to make it easier for the user (no need to run the notebook for each analysis)
2. **directionality.ipynb** : By looking at the movement of a tag through various location codes, decision rules are created to define "upstream" or "downstream" movements. If a movement is unfamiliar, it is called an "unknown" movement.
3. **time_between_detections.ipynb** : A unique detection is defined as the first time the tag is detected at a given location code. This notebook calculates the time difference between each unique detection (end datetime of the previous detection - start datetime of the current detection).
4. **pit_profiles.ipynb** : This notebook brings the directionality and time pieces (from 2 and 3) as well as adds a new column which tells us the number of times the tag was deteted a one specific location during a single, unique detection event. It is the final summary of all returning PIT tags. 

## Documentation:   
1. File preperation, data generation: [documentation.md](https://github.com/riyaeliza123/PIT-detection-patterns/blob/main/documentation/documentation.md)
2. Analysis about dead tags: [dead_tag.md](https://github.com/riyaeliza123/PIT-detection-patterns/blob/main/documentation/dead_tags.md)
<br>
## Streamlit apps created:
1. Tag summary app: [https://pit-tag-summary.streamlit.app/](https://pit-tag-summaries.streamlit.app/)
