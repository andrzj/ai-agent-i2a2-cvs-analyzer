"""
Sample CSV Generator

Creates sample CSV files for testing the CSV Analyzer AI Agent.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sales_data(n_rows=1000):
    """Generate sample sales dataset."""
    np.random.seed(42)
    
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_rows)]
    
    df = pd.DataFrame({
        'date': dates,
        'product': np.random.choice(['ProductA', 'ProductB', 'ProductC', 'ProductD'], n_rows),
        'category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], n_rows),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_rows),
        'sales_amount': np.random.normal(1000, 300, n_rows).round(2),
        'quantity': np.random.randint(1, 50, n_rows),
        'customer_age': np.random.randint(18, 80, n_rows),
        'customer_satisfaction': np.random.choice([1, 2, 3, 4, 5], n_rows, p=[0.05, 0.10, 0.20, 0.35, 0.30]),
        'discount_applied': np.random.choice([True, False], n_rows, p=[0.3, 0.7]),
        'revenue': None  # Will calculate
    })
    
    # Calculate revenue
    df['revenue'] = df['sales_amount'] * df['quantity']
    df.loc[df['discount_applied'], 'revenue'] *= 0.9  # 10% discount
    df['revenue'] = df['revenue'].round(2)
    
    # Add some outliers
    outlier_indices = np.random.choice(df.index, size=int(n_rows * 0.02), replace=False)
    df.loc[outlier_indices, 'sales_amount'] *= 5
    
    # Add some missing values
    missing_indices = np.random.choice(df.index, size=int(n_rows * 0.05), replace=False)
    df.loc[missing_indices, 'customer_age'] = np.nan
    
    return df


def generate_employee_data(n_rows=500):
    """Generate sample employee dataset."""
    np.random.seed(42)
    
    df = pd.DataFrame({
        'employee_id': range(1, n_rows + 1),
        'name': [f'Employee_{i}' for i in range(1, n_rows + 1)],
        'department': np.random.choice(['IT', 'Sales', 'HR', 'Finance', 'Marketing'], n_rows),
        'position': np.random.choice(['Junior', 'Mid', 'Senior', 'Manager', 'Director'], n_rows),
        'age': np.random.randint(22, 65, n_rows),
        'years_experience': np.random.randint(0, 40, n_rows),
        'salary': np.random.normal(60000, 20000, n_rows).round(2),
        'performance_score': np.random.uniform(1, 5, n_rows).round(2),
        'training_hours': np.random.randint(0, 100, n_rows),
        'projects_completed': np.random.randint(0, 50, n_rows),
    })
    
    # Make salary correlate with experience and position
    position_multiplier = {'Junior': 0.8, 'Mid': 1.0, 'Senior': 1.3, 'Manager': 1.6, 'Director': 2.0}
    df['salary'] = (50000 + df['years_experience'] * 1000 + 
                    df['position'].map(position_multiplier) * 20000 +
                    np.random.normal(0, 5000, n_rows)).round(2)
    
    # Add outliers
    outlier_indices = np.random.choice(df.index, size=10, replace=False)
    df.loc[outlier_indices, 'salary'] *= 2
    
    return df


def generate_customer_data(n_rows=2000):
    """Generate sample customer dataset."""
    np.random.seed(42)
    
    df = pd.DataFrame({
        'customer_id': range(1, n_rows + 1),
        'age': np.random.randint(18, 85, n_rows),
        'gender': np.random.choice(['Male', 'Female', 'Other'], n_rows),
        'income': np.random.normal(50000, 25000, n_rows).round(2),
        'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_rows),
        'marital_status': np.random.choice(['Single', 'Married', 'Divorced'], n_rows),
        'num_children': np.random.choice([0, 1, 2, 3, 4], n_rows, p=[0.3, 0.25, 0.25, 0.15, 0.05]),
        'account_balance': np.random.uniform(0, 100000, n_rows).round(2),
        'credit_score': np.random.randint(300, 850, n_rows),
        'churn': np.random.choice([0, 1], n_rows, p=[0.8, 0.2]),
    })
    
    # Make churn correlate with other factors
    df.loc[(df['credit_score'] < 500) | (df['account_balance'] < 1000), 'churn'] = \
        np.random.choice([0, 1], sum((df['credit_score'] < 500) | (df['account_balance'] < 1000)), p=[0.4, 0.6])
    
    return df


if __name__ == "__main__":
    # Generate and save sample datasets
    
    print("Generating sample datasets...")
    
    # Sales data
    sales_df = generate_sales_data(1000)
    sales_df.to_csv('../sample_data_sales.csv', index=False)
    print(f"✓ Generated sample_data_sales.csv ({len(sales_df)} rows)")
    
    # Employee data
    employee_df = generate_employee_data(500)
    employee_df.to_csv('../sample_data_employees.csv', index=False)
    print(f"✓ Generated sample_data_employees.csv ({len(employee_df)} rows)")
    
    # Customer data
    customer_df = generate_customer_data(2000)
    customer_df.to_csv('../sample_data_customers.csv', index=False)
    print(f"✓ Generated sample_data_customers.csv ({len(customer_df)} rows)")
    
    print("\nAll sample datasets generated successfully!")
    print("You can now upload these CSV files to test the agent.")
