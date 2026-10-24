"""
Script to generate rich, realistic sample datasets for the Conversational Data Analysis Assistant.
Generates:
1. ecommerce_sales.csv
2. healthcare_patients.csv
3. student_academics.csv
4. financial_tech_stocks.csv
"""

import os
import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

out_dir = os.path.join(os.path.dirname(__file__), "sample_datasets")
os.makedirs(out_dir, exist_ok=True)

# 1. E-Commerce Sales Dataset (100 rows)
regions = ["North", "South", "East", "West"]
categories = {
    "Technology": ["Laptops", "Smartphones", "Accessories", "Monitors"],
    "Furniture": ["Office Chairs", "Desks", "Bookcases", "Tables"],
    "Office Supplies": ["Paper", "Binders", "Pens", "Storage"]
}
customer_names = [
    "Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince", "Evan Wright",
    "Fiona Gallagher", "George Clark", "Hannah Abbott", "Ian Malcolm", "Julia Roberts",
    "Kevin Bacon", "Laura Croft", "Michael Scott", "Nora Fatehi", "Oscar Isaac"
]
segments = ["Consumer", "Corporate", "Home Office"]

ecom_rows = []
for i in range(1, 101):
    cat = random.choice(list(categories.keys()))
    sub_cat = random.choice(categories[cat])
    region = random.choice(regions)
    sales = round(random.uniform(20.0, 1500.0), 2)
    qty = random.randint(1, 10)
    discount = round(random.choice([0.0, 0.05, 0.1, 0.15, 0.2, 0.3]), 2)
    profit = round(sales * (random.uniform(0.05, 0.35) - discount * 0.5), 2)
    returned = random.choices(["No", "Yes"], weights=[0.88, 0.12])[0]
    
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    ecom_rows.append({
        "Order_ID": f"ORD-2024-{1000 + i}",
        "Order_Date": f"2024-{month:02d}-{day:02d}",
        "Customer_Name": random.choice(customer_names),
        "Segment": random.choice(segments),
        "Region": region,
        "Category": cat,
        "Sub_Category": sub_cat,
        "Product_Name": f"{sub_cat} Pro Model-{random.randint(10, 99)}",
        "Sales": sales,
        "Quantity": qty,
        "Discount": discount,
        "Profit": profit,
        "Return_Status": returned
    })

df_ecom = pd.DataFrame(ecom_rows)
df_ecom.to_csv(os.path.join(out_dir, "ecommerce_sales.csv"), index=False)

# 2. Healthcare Patients Dataset (100 rows)
genders = ["Male", "Female"]
smokers = ["Yes", "No"]
health_rows = []

for i in range(1, 101):
    age = random.randint(21, 78)
    gender = random.choice(genders)
    bmi = round(random.uniform(18.5, 38.0), 1)
    smoker = random.choices(smokers, weights=[0.25, 0.75])[0]
    sys_bp = random.randint(105, 165)
    chol = random.randint(140, 280)
    glucose = random.randint(75, 190)
    exercise = round(random.uniform(0.5, 8.5), 1)
    
    # Risk factor logic
    risk_score = 0
    if age > 50: risk_score += 1
    if smoker == "Yes": risk_score += 2
    if sys_bp > 135: risk_score += 1
    if chol > 220: risk_score += 1
    if glucose > 130: risk_score += 1
    
    risk_level = "High" if risk_score >= 3 else ("Moderate" if risk_score >= 2 else "Low")
    medical_cost = round(2500 + (age * 120) + (risk_score * 3500) + (2000 if smoker == "Yes" else 0) + random.uniform(-500, 1500), 2)
    
    health_rows.append({
        "Patient_ID": f"PT-{2000 + i}",
        "Age": age,
        "Gender": gender,
        "BMI": bmi,
        "Systolic_BP": sys_bp,
        "Cholesterol_mg_dL": chol,
        "Fasting_Glucose": glucose,
        "Exercise_Hours_Weekly": exercise,
        "Smoker": smoker,
        "Heart_Disease_Risk": risk_level,
        "Annual_Medical_Cost_USD": medical_cost
    })

df_health = pd.DataFrame(health_rows)
df_health.to_csv(os.path.join(out_dir, "healthcare_patients.csv"), index=False)

# 3. Student Academic Performance Dataset (100 rows)
student_rows = []
for i in range(1, 101):
    gender = random.choice(["Male", "Female"])
    study_hrs = round(random.uniform(4.0, 35.0), 1)
    attendance = round(random.uniform(60.0, 99.5), 1)
    extracurricular = random.choice(["Yes", "No"])
    prev_score = round(random.uniform(45.0, 95.0), 1)
    internet = random.choices(["Yes", "No"], weights=[0.9, 0.1])[0]
    
    final_score = round(prev_score * 0.4 + (study_hrs * 1.3) + (attendance * 0.3) + random.uniform(-6, 6), 1)
    final_score = max(35.0, min(100.0, final_score))
    
    grade = "A" if final_score >= 85 else ("B" if final_score >= 70 else ("C" if final_score >= 55 else "F"))
    passed = "Pass" if final_score >= 50 else "Fail"
    
    student_rows.append({
        "Student_ID": f"STU-{3000 + i}",
        "Gender": gender,
        "Study_Hours_Weekly": study_hrs,
        "Attendance_Percentage": attendance,
        "Extracurricular_Activities": extracurricular,
        "Previous_Exam_Score": prev_score,
        "Internet_Access_At_Home": internet,
        "Final_Exam_Score": final_score,
        "Grade": grade,
        "Pass_Status": passed
    })

df_student = pd.DataFrame(student_rows)
df_student.to_csv(os.path.join(out_dir, "student_academics.csv"), index=False)

# 4. Financial Tech Stocks Dataset (80 rows)
stocks = [
    ("AAPL", "Apple Inc.", 3400.0),
    ("MSFT", "Microsoft Corp.", 3100.0),
    ("GOOGL", "Alphabet Inc.", 2100.0),
    ("NVDA", "Nvidia Corp.", 3200.0),
    ("AMZN", "Amazon.com Inc.", 1950.0)
]
stock_rows = []
dates = pd.date_range("2024-01-01", periods=16, freq="B").strftime("%Y-%m-%d").tolist()

for ticker, company, base_cap in stocks:
    price = random.uniform(140.0, 480.0)
    for dt in dates:
        change_pct = round(random.uniform(-4.5, 4.8), 2)
        close_price = round(price * (1 + change_pct / 100), 2)
        high_price = round(max(price, close_price) + random.uniform(0.5, 5.0), 2)
        low_price = round(min(price, close_price) - random.uniform(0.5, 5.0), 2)
        volume = random.randint(15_000_000, 75_000_000)
        market_cap = round(base_cap * (close_price / price), 2)
        
        stock_rows.append({
            "Date": dt,
            "Ticker": ticker,
            "Company_Name": company,
            "Open_USD": round(price, 2),
            "High_USD": high_price,
            "Low_USD": low_price,
            "Close_USD": close_price,
            "Daily_Return_Pct": change_pct,
            "Volume": volume,
            "Market_Cap_B": market_cap
        })
        price = close_price

df_stocks = pd.DataFrame(stock_rows)
df_stocks.to_csv(os.path.join(out_dir, "financial_tech_stocks.csv"), index=False)

print(f"Generated 4 sample datasets in {out_dir}:")
print(f" - ecommerce_sales.csv: {len(df_ecom)} rows")
print(f" - healthcare_patients.csv: {len(df_health)} rows")
print(f" - student_academics.csv: {len(df_student)} rows")
print(f" - financial_tech_stocks.csv: {len(df_stocks)} rows")
