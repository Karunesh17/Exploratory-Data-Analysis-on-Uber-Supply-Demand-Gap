import os
import pandas as pd
import numpy as np

def clean_uber_data():
    raw_path = os.path.join(os.path.dirname(__file__), 'raw', 'uber_request_data.csv')
    if not os.path.exists(raw_path):
        raw_path = os.path.join('data', 'raw', 'uber_request_data.csv')
    
    print(f"Loading raw data from: {raw_path}")
    df = pd.read_csv(raw_path)
    
    # Standardize column names
    col_map = {
        'Request id': 'request_id',
        'Pickup point': 'pickup_point',
        'Driver id': 'driver_id',
        'Status': 'status',
        'Request timestamp': 'request_timestamp',
        'Drop timestamp': 'drop_timestamp'
    }
    df = df.rename(columns=col_map)
    
    # Convert timestamps
    df['request_timestamp'] = pd.to_datetime(df['request_timestamp'], dayfirst=True, format='mixed')
    df['drop_timestamp'] = pd.to_datetime(df['drop_timestamp'], dayfirst=True, format='mixed')
    
    # Feature Engineering
    df['request_date'] = df['request_timestamp'].dt.date
    df['request_hour'] = df['request_timestamp'].dt.hour
    df['day_of_week'] = df['request_timestamp'].dt.dayofweek
    df['day_name'] = df['request_timestamp'].dt.day_name()
    
    # Time slot categorization
    def assign_time_slot(hour):
        if 0 <= hour < 5:
            return 'Early Morning (12 AM - 5 AM)'
        elif 5 <= hour < 10:
            return 'Morning Rush (5 AM - 10 AM)'
        elif 10 <= hour < 17:
            return 'Midday (10 AM - 5 PM)'
        elif 17 <= hour < 22:
            return 'Evening Rush (5 PM - 10 PM)'
        else:
            return 'Late Night (10 PM - 12 AM)'
            
    df['time_slot'] = df['request_hour'].apply(assign_time_slot)
    
    # Binary status flags
    df['is_completed'] = (df['status'] == 'Trip Completed').astype(int)
    df['is_cancelled'] = (df['status'] == 'Cancelled').astype(int)
    df['is_no_cars'] = (df['status'] == 'No Cars Available').astype(int)
    df['is_unfulfilled'] = (df['status'].isin(['Cancelled', 'No Cars Available'])).astype(int)
    
    # Trip duration in minutes for completed trips
    df['trip_duration_mins'] = np.where(
        df['is_completed'] == 1,
        (df['drop_timestamp'] - df['request_timestamp']).dt.total_seconds() / 60.0,
        np.nan
    )
    
    # Save cleaned dataset
    out_path = os.path.join(os.path.dirname(__file__), 'uber_cleaned_data.csv')
    df.to_csv(out_path, index=False)
    print(f"Cleaned dataset saved to: {out_path} (Shape: {df.shape})")
    
    return df

if __name__ == '__main__':
    clean_uber_data()
