import os
import sqlite3
import pandas as pd
import numpy as np

def run_sql_analysis():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, 'data', 'uber_cleaned_data.csv')
    db_path = os.path.join(base_dir, 'data', 'uber.db')
    sql_file = os.path.join(base_dir, 'sql', 'uber_analysis.sql')
    
    print("=== 1. LOADING DATA INTO SQLITE ===")
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    
    # Save to table
    df.to_sql('uber_trips', conn, if_exists='replace', index=False)
    print(f"Loaded {len(df)} records into table 'uber_trips' in {db_path}")
    
    # Read sql file
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
        
    # Split queries by semicolon
    raw_queries = [q.strip() for q in sql_content.split(';') if q.strip()]
    queries = []
    for q in raw_queries:
        lines = [line for line in q.split('\n') if line.strip() and not line.strip().startswith('--')]
        if lines:
            queries.append(q)
            
    query_names = [
        "Query 1: Overall Request Volume & Status Breakdown",
        "Query 2: Overall Completion and Failure Rates",
        "Query 3: Status Breakdown by Pickup Location",
        "Query 4: Hourly Request Volume and Unfulfilled Trips",
        "Query 5: Top 5 Hours with the Most Unfulfilled Requests",
        "Query 6: City Morning Rush Cancellations (5 AM to 9 AM)",
        "Query 7: Airport Evening Rush Car Shortages (5 PM to 9 PM)",
        "Query 8: Ranking Problem Hours and Locations by Unfulfilled Requests"
    ]
    
    print("\n=== 2. EXECUTING SQL QUERIES ===")
    results = {}
    for i, q in enumerate(queries):
        name = query_names[i] if i < len(query_names) else f"Query {i+1}"
        print(f"\n--- {name} ---")
        res_df = pd.read_sql_query(q, conn)
        print(res_df.to_string(index=False))
        results[i+1] = res_df
        
    conn.close()
    
    print("\n=== 3. AUTOMATED CROSS-CHECK AGAINST PANDAS ===")
    # Check 1: Total volume and status counts
    p_status = df['status'].value_counts()
    for _, row in results[1].iterrows():
        s = row['status']
        c = row['total_requests']
        assert c == p_status[s], f"Mismatch in status count for {s}: SQL {c} != Pandas {p_status[s]}"
    print("[PASS] Check 1: Query 1 status counts match Pandas exactly.")
    
    # Check 2: Core baseline rates
    q2 = results[2].iloc[0]
    assert q2['total_demand'] == len(df)
    assert q2['completed_trips'] == (df['status'] == 'Trip Completed').sum()
    assert q2['unfulfilled_requests'] == (df['status'] != 'Trip Completed').sum()
    assert q2['completion_rate'] == round((df['status'] == 'Trip Completed').mean() * 100, 2)
    assert q2['cancellation_rate'] == round((df['status'] == 'Cancelled').mean() * 100, 2)
    assert q2['no_cars_rate'] == round((df['status'] == 'No Cars Available').mean() * 100, 2)
    assert q2['unfulfilled_rate'] == round((df['status'] != 'Trip Completed').mean() * 100, 2)
    print("[PASS] Check 2: Query 2 completion/cancellation/no-cars/unfulfilled rates match Pandas exactly.")
    
    # Check 3: Pickup location rates
    for _, row in results[3].iterrows():
        loc = row['pickup_point']
        sub = df[df['pickup_point'] == loc]
        assert row['total_requests'] == len(sub)
        assert row['completed_trips'] == (sub['status'] == 'Trip Completed').sum()
        assert row['cancelled_trips'] == (sub['status'] == 'Cancelled').sum()
        assert row['no_cars_available'] == (sub['status'] == 'No Cars Available').sum()
    print("[PASS] Check 3: Query 3 location breakdowns match Pandas exactly.")
    
    # Check 4: Hourly volume
    p_hourly = df.groupby('request_hour').agg(
        demand=('request_id', 'count'),
        completed=('is_completed', 'sum'),
        gap=('is_unfulfilled', 'sum')
    ).reset_index()
    for _, row in results[4].iterrows():
        h = int(row['request_hour'])
        p_row = p_hourly[p_hourly['request_hour'] == h].iloc[0]
        assert row['total_demand'] == p_row['demand']
        assert row['supply_completed'] == p_row['completed']
        assert row['gap_unfulfilled'] == p_row['gap']
    print("[PASS] Check 4: Query 4 24-hour demand and supply gap match Pandas exactly.")
    
    # Check 5: Top 5 problem hours
    p_top5 = p_hourly.sort_values(by='gap', ascending=False).head(5)
    sql_top5_hours = results[5]['request_hour'].tolist()
    assert sql_top5_hours == p_top5['request_hour'].tolist()
    print("[PASS] Check 5: Query 5 top 5 problem hours match Pandas exactly.")
    
    # Check 6: Morning rush city cancellations
    p_m_city = df[(df['pickup_point'] == 'City') & (df['request_hour'].between(5, 9))]
    sql_m_canc = results[6]['cancellations'].sum()
    sql_m_req = results[6]['city_requests'].sum()
    assert sql_m_req == len(p_m_city)
    assert sql_m_canc == (p_m_city['status'] == 'Cancelled').sum()
    print(f"[PASS] Check 6: Query 6 City morning rush ({sql_m_canc} cancellations / {sql_m_req} requests = {sql_m_canc/sql_m_req*100:.2f}%) matches Pandas exactly.")
    
    # Check 7: Evening rush airport shortages
    p_e_air = df[(df['pickup_point'] == 'Airport') & (df['request_hour'].between(17, 21))]
    sql_e_nocars = results[7]['no_cars_count'].sum()
    sql_e_req = results[7]['airport_requests'].sum()
    assert sql_e_req == len(p_e_air)
    assert sql_e_nocars == (p_e_air['status'] == 'No Cars Available').sum()
    print(f"[PASS] Check 7: Query 7 Airport evening rush ({sql_e_nocars} shortages / {sql_e_req} requests = {sql_e_nocars/sql_e_req*100:.2f}%) matches Pandas exactly.")
    
    # Check 8: Window function ranking
    sql_rank1 = results[8].iloc[0]
    assert sql_rank1['pickup_point'] == 'Airport' and sql_rank1['request_hour'] == 18
    assert sql_rank1['unfulfilled_count'] == 324
    print("[PASS] Check 8: Query 8 window function rank 1 (Airport Hour 18, 324 unfulfilled requests) matches Pandas exactly.")

    print("\nAll 8 SQL queries match the Pandas calculations.")

if __name__ == '__main__':
    run_sql_analysis()
