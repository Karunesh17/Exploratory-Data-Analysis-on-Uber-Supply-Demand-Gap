# 🚖 Uber Supply-Demand Gap Analysis

A comprehensive exploratory data analysis (EDA) project examining Uber's operational challenges with supply-demand imbalances, driver cancellations, and car unavailability across different time slots and pickup locations.

## 📋 Table of Contents
- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Key Findings](#key-findings)
- [Root Causes Analysis](#root-causes-analysis)
- [Business Recommendations](#business-recommendations)
- [Visualizations](#visualizations)
- [Installation](#installation)
- [Usage](#usage)
- [Technologies Used](#technologies-used)

## 📊 Overview

This project analyzes Uber ride request data to identify and understand supply-demand imbalances, particularly focusing on:
- **High cancellation rates** from drivers
- **Car unavailability** during peak demand periods
- **Time slot patterns** with significant gaps between supply and demand
- **Location-specific issues** (City → Airport vs Airport → City)

The analysis reveals critical operational inefficiencies that directly impact revenue and customer satisfaction.

## 🎯 Problem Statement

Uber faces significant operational challenges:

1. **Driver Cancellations** - Drivers frequently cancel ride requests, reducing completed trips
2. **No Cars Available** - Insufficient driver supply during peak demand periods
3. **Revenue Loss** - Unmet demand and cancellations result in lost revenue opportunities
4. **Inconsistent Service** - Supply doesn't scale proportionally with demand across time slots

The objective is to identify root causes and develop data-driven recommendations to address these supply-demand gaps.

## 📁 Dataset

The dataset contains **6,745 Uber ride request records** with the following attributes:

| Column | Type | Description |
|--------|------|-------------|
| Request ID | int64 | Unique identifier for each ride request |
| Pickup Point | object | Location type (City or Airport) |
| Request Timestamp | object | Date and time of ride request |
| Drop Timestamp | object | Date and time of ride completion |
| Driver ID | float64 | Unique driver identifier |
| Status | object | Trip outcome (Completed, Cancelled by Driver, No Cars Available) |

### Data Quality
- **Total Records**: 6,745 entries
- **Missing Values**: 
  - Driver ID: 2,650 missing (38.3%)
  - Drop Timestamp: 3,914 missing (58%)
- **Data Coverage**: Request and Pickup point have complete data
- **Duplicate Records**: 0

### Status Distribution
- **Trip Completed**: ~42% of requests
- **Cancelled by Driver**: Significant portion of failures
- **No Cars Available**: High occurrence during peak hours
- **Overall Success Rate**: ~42% (concerning metric)

## 📂 Project Structure

```
├── source.ipynb                    # Main Jupyter Notebook with full EDA
├── uber_cleaned_data.csv           # Cleaned and processed dataset
├── requirements.txt                # Project dependencies
├── .gitignore                      # Git ignore configuration
└── README.md                       # Project documentation
```

## 🔍 Key Findings

### 1. Temporal Patterns

**Peak Demand Hours:**
- **Morning Peak**: 5:00 AM - 9:00 AM (City to Airport)
- **Evening Peak**: 5:00 PM - 10:00 PM (Airport to City)
- **Late Night**: 10:00 PM - 11:00 PM (Highest request volume: 184 requests)
- **Off-Peak**: 3:00 AM - 5:00 AM (Lowest demand)

**Completion Rates by Time Slot:**
- Peak hours show significantly lower completion rates
- Early morning (5-9 AM) has the worst supply-demand gap
- Night slots (10 PM onwards) also show critical gaps

### 2. Location-Specific Issues

**City to Airport (Morning):**
- High demand from 5-10 AM
- High driver cancellation rates
- Root cause: Lower return demand (fewer incoming flights)
- Impact: Major revenue loss during morning commute

**Airport to City (Evening/Night):**
- Peak demand 5-10 PM and late night
- "No Cars Available" status is dominant
- Root cause: Insufficient driver availability
- Impact: Lost evening commute revenue

### 3. Supply-Demand Gap Analysis

- **Total Demand**: 6,745 ride requests
- **Total Supply**: ~2,831 completed trips
- **Overall Gap**: 58% of requests unfulfilled
- **Highest Gap**: Early morning (5-9 AM) and late night (10 PM-11 PM)
- **Lowest Gap**: Midday hours (10 AM - 4 PM)

### 4. Cancellation Analysis

- **Driver Cancellations** concentrated in:
  - Early morning hours (long wait times for return trips)
  - City pickup points (distance/duration concerns)
  - Days with low airport traffic

- **Pattern**: Drivers cancel when unprofitable trips are likely (City → Airport, low return demand)

### 5. Completion Rate Insights

- **Best Performance**: Midday hours (40-45% completion)
- **Worst Performance**: Early morning and late night (25-35% completion)
- **Weekend Effect**: 45% of unfulfilled requests occur during weekends
- **Average Trips/Driver**: 0.83 trips (indicating underutilization)

## 🔎 Root Causes Analysis

### 1. Early Morning Gap (5-9 AM) - City to Airport

**Why it happens:**
- High demand for airport travel in morning
- Few return flights arriving early morning = low return demand
- Drivers reluctant to make long city-airport trip without return fare
- Limited driver availability that early

**Evidence:**
- 58% completion rate during peak morning hours
- Significant driver cancellation pattern
- Long wait times for return passengers

### 2. Evening/Night Gap (5-10 PM & 10 PM-11 PM) - Airport to City

**Why it happens:**
- High passenger arrival volume from flights
- Insufficient drivers positioned at airport
- Drivers don't relocate to airport proactively
- Surge pricing doesn't compensate for location inconvenience

**Evidence:**
- "No Cars Available" is primary issue (not cancellations)
- Persistent gap even during high demand
- Driver-to-request ratio critically low

### 3. General Supply-Demand Mismatch

- Driver supply doesn't scale with demand fluctuations
- Drivers concentrate on profitable routes, abandoning airport routes
- No predictive deployment mechanism
- Shift timings don't align with natural demand cycles

## 💡 Business Recommendations

### 1. **Dynamic Driver Incentive Program**
Implement surge pricing and bonuses during critical gaps:
- **Early Morning (5-9 AM)**: 1.5-2x fare multiplier for City→Airport trips + guaranteed return bonus
- **Late Night (10 PM-11 PM)**: 1.5x multiplier for Airport→City trips
- **Estimated Impact**: Reduce morning gap by 25-30%, evening gap by 20-25%

### 2. **Airport-Dedicated Driver Shifts**
Create dedicated driver pools stationed at airport:
- Recruit drivers living near airport to avoid long travel time
- Offer premium per-trip bonus for airport focus
- Create 24/7 availability model for airport pickups
- **Estimated Impact**: Reduce "No Cars Available" by 40%

### 3. **Ride Pooling Initiative**
Incentivize customer pooling during peak hours:
- Offer 20-30% discounts for shared City→Airport rides
- Create carpooling incentive for morning commuters
- Bundle multiple rider requests to improve driver profitability
- **Estimated Impact**: Increase vehicle utilization by 35-40%

### 4. **Shift Timing Realignment**
Adjust operational cycles based on demand patterns:
- Change "end-of-day" reset from midnight to 4:00 AM
- Aligns with natural business cycles and low-demand period
- Enables better shift planning for peak hours
- **Estimated Impact**: Improve overall operational efficiency by 15%

### 5. **Predictive Analytics & Real-time Deployment**
Implement machine learning for supply optimization:
- Predict demand by time slot and location
- Pre-position drivers 30-60 minutes before peak demand
- Real-time tracking and dynamic routing
- Alert system for high-gap periods
- **Estimated Impact**: Close 30-35% of overall gap within 6 months

### 6. **Targeted Marketing & Demand Smoothing**
Reduce peak hour concentration:
- Promote off-peak travel with discounts (10 AM - 3 PM)
- Offer advance booking discounts to spread demand
- Target corporate partnerships for flexible travel times
- **Estimated Impact**: Shift 10-15% of demand to off-peak hours

## 📈 Visualizations

This project includes comprehensive visualizations:

1. **Request Frequency by Time Slot** - Hourly demand distribution
2. **Status Distribution** - Pie/bar chart of Completed vs Cancelled vs No Cars
3. **City vs Airport Comparison** - Location-specific demand patterns
4. **Supply-Demand Gap Trends** - Time-series showing gap evolution
5. **Peak Hour Analysis** - Focusing on critical morning and evening periods
6. **Cancellation Pattern Heatmap** - Time and location intersection analysis
7. **Completion Rate Trends** - Performance metrics across time slots
8. **Weekend vs Weekday Comparison** - Demand pattern differences

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- Jupyter Notebook
- pip or conda

### Required Libraries
```bash
pip install pandas numpy matplotlib seaborn
```

### Clone Repository
```bash
git clone https://github.com/Karunesh17/Exploratory-Data-Analysis-on-Uber-Supply-Demand-Gap.git
cd Exploratory-Data-Analysis-on-Uber-Supply-Demand-Gap
```

## 🚀 Usage

### Run the Jupyter Notebook
```bash
jupyter notebook source.ipynb
```

### Key Code Sections

**Data Loading & Initial Exploration**
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("uber_cleaned_data.csv")
df.info()
df.describe()
```

**Extracting Time-Based Features**
```python
df['Request timestamp'] = pd.to_datetime(df['Request timestamp'])
df['pickup_hour'] = df['Request timestamp'].dt.hour
df['pickup_date'] = df['Request timestamp'].dt.date
df['day_of_week'] = df['Request timestamp'].dt.dayofweek
```

**Supply-Demand Gap Calculation**
```python
demand = df.groupby('pickup_hour')['Request ID'].count()
supply = df[df['Status'] == 'Trip Completed'].groupby('pickup_hour')['Request ID'].count()
gap = demand - supply
```

**Cancellation Analysis by Time Slot**
```python
cancellations = df[df['Status'] == 'Cancelled by Driver'].groupby('pickup_hour').size()
no_cars = df[df['Status'] == 'No Cars Available'].groupby('pickup_hour').size()
```

**Location-Specific Analysis**
```python
city_airport = df[df['Pickup point'] == 'City'].groupby('pickup_hour')['Status'].value_counts()
airport_city = df[df['Pickup point'] == 'Airport'].groupby('pickup_hour')['Status'].value_counts()
```

## 📊 Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3** | Core programming language |
| **Pandas** | Data manipulation and analysis |
| **NumPy** | Numerical computations |
| **Matplotlib** | Static data visualizations |
| **Seaborn** | Advanced statistical visualizations |
| **Jupyter Notebook** | Interactive development and reporting |

## 📈 Expected Business Impact

Based on recommendations implementation:

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Overall Trip Completion Rate | 42% | 58-62% | 6 months |
| Morning Gap Reduction | - | 25-30% | 3 months |
| Evening Gap Reduction | - | 20-25% | 3 months |
| Driver Utilization | 0.83 trips/driver | 1.3-1.5 | 6 months |
| Weekend Performance | 45% gap | 30-35% gap | 6 months |

## 🔗 Resources

- [Kaggle - Similar Uber Dataset](https://www.kaggle.com/goyalshalini93/uber-supply-demand-gap-analysis-eda)
- [Uber Engineering Blog](https://www.uber.com/en-IN/blog/)
- [Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/)

## 📧 Contact & Support

For questions or feedback:
- **GitHub**: [Karunesh17](https://github.com/Karunesh17)
- **Project Repository**: [Exploratory-Data-Analysis-on-Uber-Supply-Demand-Gap](https://github.com/Karunesh17/Exploratory-Data-Analysis-on-Uber-Supply-Demand-Gap)

## 📜 License

This project is provided as-is for educational and analytical purposes.

## 🎓 Learning Outcomes

By exploring this project, you'll learn:
- ✅ Exploratory Data Analysis (EDA) techniques
- ✅ Time-series data analysis and visualization
- ✅ Supply chain optimization concepts
- ✅ Business problem-solving with data
- ✅ Data-driven recommendation making
- ✅ Pandas data manipulation and groupby operations
- ✅ Matplotlib and Seaborn visualization

---

**Project Status**: Complete ✅ | **Last Updated**: 2024 | **Difficulty Level**: Intermediate

**Key Takeaway**: This analysis demonstrates how data-driven insights can identify operational bottlenecks and guide strategic business decisions for a mobility platform like Uber.
