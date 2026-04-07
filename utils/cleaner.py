"""
utils/cleaner.py — Data cleaning utility functions.

Provides functions for handling missing values, removing duplicates,
inferring data types, and removing outliers.
"""

import pandas as pd
import numpy as np


def handle_missing(df: pd.DataFrame, strategy: str = "drop_rows") -> tuple:
    """
    Handle missing values in a dataframe.
    
    Args:
        df: pandas DataFrame
        strategy: 'drop_rows', 'drop_cols', 'fill_mean', 'fill_median', 
                 'fill_mode', 'fill_zero'
    
    Returns:
        (new_df, message) tuple
    """
    if df.isnull().sum().sum() == 0:
        return df.copy(), "No missing values found."
    
    new_df = df.copy()
    
    if strategy == "drop_rows":
        new_df = new_df.dropna()
        return new_df, f"Removed rows with missing values. New shape: {new_df.shape}"
    
    elif strategy == "drop_cols":
        threshold = 0.5
        cols_to_drop = new_df.columns[new_df.isnull().mean() > threshold]
        new_df = new_df.drop(columns=cols_to_drop)
        return new_df, f"Dropped columns with >50% missing. New shape: {new_df.shape}"
    
    elif strategy == "fill_mean":
        numeric_cols = new_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if new_df[col].isnull().any():
                new_df[col].fillna(new_df[col].mean(), inplace=True)
        return new_df, "Filled numeric columns with mean."
    
    elif strategy == "fill_median":
        numeric_cols = new_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if new_df[col].isnull().any():
                new_df[col].fillna(new_df[col].median(), inplace=True)
        return new_df, "Filled numeric columns with median."
    
    elif strategy == "fill_mode":
        for col in new_df.columns:
            if new_df[col].isnull().any():
                mode_val = new_df[col].mode()
                if len(mode_val) > 0:
                    new_df[col].fillna(mode_val[0], inplace=True)
        return new_df, "Filled columns with mode."
    
    elif strategy == "fill_zero":
        numeric_cols = new_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            new_df[col].fillna(0, inplace=True)
        return new_df, "Filled numeric columns with 0."
    
    return new_df, "No action taken."


def remove_duplicates(df: pd.DataFrame) -> tuple:
    """
    Remove duplicate rows from a dataframe.
    
    Args:
        df: pandas DataFrame
    
    Returns:
        (new_df, message) tuple
    """
    dup_count = df.duplicated().sum()
    
    if dup_count == 0:
        return df.copy(), "No duplicate rows found."
    
    new_df = df.drop_duplicates()
    return new_df, f"Removed {dup_count} duplicate row(s). New shape: {new_df.shape}"


def infer_dtypes(df: pd.DataFrame) -> tuple:
    """
    Infer and convert data types where possible.
    
    Args:
        df: pandas DataFrame
    
    Returns:
        (new_df, message) tuple
    """
    new_df = df.copy()
    
    changes = 0
    for col in new_df.columns:
        if new_df[col].dtype == 'object':
            try:
                new_df[col] = pd.to_numeric(new_df[col])
                changes += 1
            except (ValueError, TypeError):
                pass
    
    return new_df, f"Inferred dtypes. {changes} column(s) converted."


def remove_outliers_iqr(df: pd.DataFrame, column: str = None) -> tuple:
    """
    Remove outliers using the Interquartile Range (IQR) method.
    
    Args:
        df: pandas DataFrame
        column: specific column to check for outliers
    
    Returns:
        (new_df, message) tuple
    """
    new_df = df.copy()
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return new_df, "No numeric columns found."
    
    if column and column not in numeric_cols:
        return new_df, f"Column '{column}' is not numeric."
    
    cols_to_check = [column] if column else numeric_cols
    outlier_mask = pd.Series(False, index=new_df.index)
    
    for col in cols_to_check:
        Q1 = new_df[col].quantile(0.25)
        Q3 = new_df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outlier_mask |= (new_df[col] < lower) | (new_df[col] > upper)
    
    outlier_count = outlier_mask.sum()
    new_df = new_df[~outlier_mask]
    
    if outlier_count == 0:
        return new_df, "No outliers detected."
    
    return new_df, f"Removed {outlier_count} outlier row(s). New shape: {new_df.shape}"
