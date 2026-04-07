"""
utils/insights.py — Statistical insight generation utilities.
"""

import pandas as pd
import numpy as np


def generate_insights(df: pd.DataFrame) -> list[str]:
    """
    Generate statistical insights from a DataFrame.
    
    Args:
        df: Input DataFrame to analyze
        
    Returns:
        List of insight strings (one per line for display)
    """
    if df is None or df.empty:
        return ["No data available."]
    
    lines = []
    lines.append(f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    lines.append("")
    
    # Column names and types
    lines.append("Columns & Types:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        lines.append(f"  {col}: {dtype}")
    lines.append("")
    
    # Numeric columns statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        lines.append("Numeric Summary Statistics:")
        for col in numeric_cols:
            mean_val = df[col].mean()
            median_val = df[col].median()
            std_val = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()
            lines.append(f"  {col}:")
            lines.append(f"    Mean: {mean_val:.4f}, Median: {median_val:.4f}")
            lines.append(f"    Std Dev: {std_val:.4f}")
            lines.append(f"    Range: [{min_val:.4f}, {max_val:.4f}]")
        lines.append("")
    
    # Missing values
    lines.append("Missing Values:")
    missing = df.isnull().sum()
    has_missing = False
    for col, count in missing[missing > 0].items():
        lines.append(f"  {col}: {count} ({100*count/len(df):.1f}%)")
        has_missing = True
    if not has_missing:
        lines.append("  None - all data is complete!")
    
    return lines
