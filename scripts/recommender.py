import pandas as pd
import argparse
import os

def recommend_funds(risk_appetite):
    file_path = os.path.join('data', 'processed', '07_scheme_performance.csv')
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    df = pd.read_csv(file_path)
    
    # Map user input to fund risk grades
    appetite = risk_appetite.strip().lower()
    if appetite == 'low':
        target_grades = ['Low']
    elif appetite == 'moderate':
        target_grades = ['Moderate', 'Moderately High']
    elif appetite == 'high':
        target_grades = ['High', 'Very High']
    else:
        print("Invalid risk appetite. Please choose from: Low, Moderate, High.")
        return

    # Filter and rank
    filtered = df[df['risk_grade'].isin(target_grades)]
    if filtered.empty:
        print(f"No funds found matching risk profile: {risk_appetite}")
        return

    # Sort by Sharpe Ratio descending
    top_3 = filtered.sort_values(by='sharpe_ratio', ascending=False).head(3)

    print(f"\n{'='*60}")
    print(f"TOP 3 FUND RECOMMENDATIONS (Risk: {risk_appetite.upper()})")
    print(f"{'='*60}")
    
    for i, (_, row) in enumerate(top_3.iterrows(), 1):
        print(f"\n{i}. {row['scheme_name']}")
        print(f"   Category: {row['category']} | Risk Grade: {row['risk_grade']}")
        print(f"   Sharpe Ratio: {row['sharpe_ratio']:.2f}")
        print(f"   3Yr Return: {row['return_3yr_pct']}% | Expense Ratio: {row['expense_ratio_pct']}%")
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Mutual Fund Recommender")
    parser.add_argument('risk', type=str, choices=['Low', 'Moderate', 'High'], help="Your risk appetite")
    args = parser.parse_args()
    
    recommend_funds(args.risk)
