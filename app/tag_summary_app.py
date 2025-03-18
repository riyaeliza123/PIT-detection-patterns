import streamlit as st
import pandas as pd

detection_counts = pd.read_csv("data/most_detected_tags.csv")
dwell_loc = pd.read_csv("data/loc_code_detection_patterns.csv")
info = pd.read_csv("data/additional_tag_info.csv")

# Convert date columns to datetime
dwell_loc["start_date"] = pd.to_datetime(dwell_loc["start_date"])
dwell_loc["end_date"] = pd.to_datetime(dwell_loc["end_date"])

# Streamlit UI
st.title("Tag ID Information Lookup")

tag = st.number_input("Enter Tag ID:", min_value=0.0, format="%.12f")

if st.button("Search"):
    if tag in detection_counts["tag_id"].values:
        st.write(f"### Tag ID: {tag}")
        st.write(f"**Total number of detections:** {detection_counts[detection_counts['tag_id'] == tag]['count'].iloc[0]}")
        st.write(f"**Found in cleaning table?** {detection_counts[detection_counts['tag_id'] == tag]['in_cleaning_table'].iloc[0]}")

        info_tag = info[info.tag_id_long == tag]
        if not info_tag.empty:
            st.write(f"**Species:** {info_tag['species'].iloc[0]}")
            st.write(f"**Stock:** {info_tag['updated_stock'].iloc[0]}")
            st.write(f"**Source:** {info_tag['source'].iloc[0]}")
            st.write(f"**Tag Date:** {info_tag['tag_date'].iloc[0]}")

        tag_dwell = dwell_loc[dwell_loc.tag_id == tag]
        if not tag_dwell.empty:
            st.write(f"**First detected:** {tag_dwell['start_date'].min()}")
            st.write(f"**Last detected:** {tag_dwell['end_date'].max()}")
            st.write("### Details of each detection:")
            st.dataframe(tag_dwell)
        else:
            st.write("No dwell location data found for this tag.")
    else:
        st.error("Tag ID not found in detection counts.")