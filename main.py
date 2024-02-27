import json
import pandas as pd
from datetime import datetime
from dateutil import parser


# Load your JSON data
with open('Takeout/Location History (Timeline)/Semantic Location History/2024/2024_FEBRUARY.json') as f:
    data = json.load(f)

# Extracting the relevant information
activities = []
datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"


for obj in data['timelineObjects']:
    if 'activitySegment' in obj:
        segment = obj['activitySegment']
        start_time = parser.parse(segment['duration']['startTimestamp'])
        end_time = parser.parse(segment['duration']['endTimestamp'])


        distance = segment['distance']
        activity_type = segment['activityType']
        activities.append({
            'start_time': start_time,
            'end_time': end_time,
            'distance': distance,
            'activity_type': activity_type
        })

# Converting to DataFrame for easier analysis
df = pd.DataFrame(activities)

# Adding month and year for grouping
df['month'] = df['start_time'].dt.month
df['year'] = df['start_time'].dt.year

# Grouping by month and year to get monthly stats
monthly_distance = df.groupby(['year', 'month'])['distance'].sum().reset_index(name='total_distance')
activity_distribution = df.groupby(['activity_type']).size().reset_index(name='counts')

print(monthly_distance)
print(activity_distribution)
