import json
import pandas as pd
from dateutil import parser
import matplotlib.pyplot as plt

# Load your JSON data
with open('Takeout/Location History (Timeline)/Semantic Location History/2024/2024_FEBRUARY.json') as f:
    data = json.load(f)

# List of dates to skip in the format 'YYYY-MM-DD'
dates_to_skip = ['2024-02-05', '2024-02-10']  # Example dates to skip

# Extracting the relevant information
passenger_vehicle_activities = []

for obj in data['timelineObjects']:
    if 'activitySegment' in obj:
        segment = obj['activitySegment']
        activity_type = segment['activityType']
        
        # Check if the activity type is "IN_PASSENGER_VEHICLE"
        if activity_type == "IN_PASSENGER_VEHICLE":
            start_time = parser.parse(segment['duration']['startTimestamp'])
            
            # Skip activities on specified dates
            if start_time.strftime('%Y-%m-%d') in dates_to_skip:
                continue  # Skip this iteration and don't add the activity
            
            end_time = parser.parse(segment['duration']['endTimestamp'])
            distance = segment['distance']

            passenger_vehicle_activities.append({
                'date': start_time.date(),
                'distance': distance * 0.000621371,  # Convert meters to miles
            })

# Converting to DataFrame for easier analysis
df = pd.DataFrame(passenger_vehicle_activities)

# Aggregating distance by day
daily_distance = df.groupby('date')['distance'].sum().reset_index()

# Calculate total distance
total_distance_miles = daily_distance['distance'].sum()

# Plotting
plt.figure(figsize=(10, 6))
plt.bar(daily_distance['date'].astype(str), daily_distance['distance'], color='blue')
plt.title(f'Daily Distance Traveled in Passenger Vehicle (Miles)\nTotal: {total_distance_miles:.2f} Miles')
plt.xlabel('Date')
plt.ylabel('Distance (Miles)')
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels
plt.show()
