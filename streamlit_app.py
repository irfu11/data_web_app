"""
DataLens Analytics Dashboard — Streamlit Version
Web-based data analytics platform with Groq AI integration
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO, StringIO
import os

# Configure Streamlit
st.set_page_config(
    page_title="DataLens Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

@st.cache_data
def load_data(file):
    """Load CSV or Excel file"""
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file format. Please use CSV or Excel.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


def generate_stats_report(df):
    """Generate statistical insights"""
    if df is None or df.empty:
        return ["No data available."]
    
    lines = []
    lines.append(f"📊 Dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")
    lines.append("")
    
    lines.append("🔍 **Column Information:**")
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        lines.append(f"  • **{col}** ({dtype}) — {null_count} missing values")
    lines.append("")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        lines.append("📈 **Numeric Statistics:**")
        for col in numeric_cols:
            mean_val = df[col].mean()
            median_val = df[col].median()
            std_val = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()
            lines.append(f"  • **{col}**: μ={mean_val:.2f}, σ={std_val:.2f}, min={min_val:.2f}, max={max_val:.2f}")
    
    lines.append("")
    lines.append(f"❌ **Missing Values:** {df.isnull().sum().sum()} cells")
    lines.append(f"🔄 **Duplicate Rows:** {df.duplicated().sum()}")
    
    return lines


def clean_data(df, operation, **kwargs):
    """Apply cleaning operation"""
    df_clean = df.copy()
    
    if operation == "drop_rows_na":
        df_clean = df_clean.dropna()
    elif operation == "drop_cols_na":
        cols_to_drop = df_clean.columns[df_clean.isnull().sum() / len(df_clean) > 0.5]
        df_clean = df_clean.drop(columns=cols_to_drop)
    elif operation == "fill_mean":
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
    elif operation == "fill_median":
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
    elif operation == "fill_zero":
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
    elif operation == "remove_duplicates":
        df_clean = df_clean.drop_duplicates()
    elif operation == "infer_dtypes":
        df_clean = df_clean.infer_objects()
    elif operation == "remove_outliers":
        col = kwargs.get('column')
        if col and col in df_clean.columns:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            df_clean = df_clean[(df_clean[col] >= Q1 - 1.5*IQR) & (df_clean[col] <= Q3 + 1.5*IQR)]
    
    return df_clean


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR - FILE UPLOAD & SETTINGS
# ═══════════════════════════════════════════════════════════════

st.sidebar.title("📂 DataLens Analytics")
st.sidebar.markdown("---")

# File upload
uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset (CSV or Excel)",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.session_state['df'] = df
        st.session_state['df_raw'] = df.copy()
        st.sidebar.success(f"✅ Loaded: {uploaded_file.name}")
        st.sidebar.info(f"📊 {df.shape[0]:,} rows × {df.shape[1]} columns")
else:
    st.sidebar.info("👆 Upload a file to begin")

st.sidebar.markdown("---")

# Groq API Config
st.sidebar.subheader("🤖 Groq AI Configuration")
api_key = st.sidebar.text_input("API Key", type="password", help="Get your key at console.groq.com")
if api_key:
    st.session_state['groq_api_key'] = api_key
    st.sidebar.success("✅ API Key stored")

# ═══════════════════════════════════════════════════════════════
#  MAIN CONTENT - TABS
# ═══════════════════════════════════════════════════════════════

if 'df' in st.session_state:
    df = st.session_state['df']
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "🧹 Cleaning",
        "📈 Visualize",
        "🔗 Correlation",
        "💡 Insights",
        "📤 Export"
    ])
    
    # ═══════════════════════════════════════════════════════════════
    #  TAB 1: OVERVIEW
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        st.header("Dataset Overview")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Rows", f"{df.shape[0]:,}")
        with col2:
            st.metric("Columns", df.shape[1])
        with col3:
            num_cols = df.select_dtypes(include=np.number).shape[1]
            st.metric("Numeric", num_cols)
        with col4:
            cat_cols = df.select_dtypes(include="object").shape[1]
            st.metric("Categorical", cat_cols)
        with col5:
            missing = df.isnull().sum().sum()
            st.metric("Missing", missing)
        with col6:
            duplicates = df.duplicated().sum()
            st.metric("Duplicates", duplicates)
        
        st.subheader("Data Preview")
        st.dataframe(df.head(100), use_container_width=True)
        
        st.subheader("Column Information")
        col_info = []
        for col in df.columns:
            col_info.append({
                "Column": col,
                "Type": str(df[col].dtype),
                "Non-Null": df[col].count(),
                "Unique": df[col].nunique(),
                "Missing": df[col].isnull().sum()
            })
        st.dataframe(pd.DataFrame(col_info), use_container_width=True)
    
    # ═══════════════════════════════════════════════════════════════
    #  TAB 2: DATA CLEANING
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        st.header("Data Cleaning")
        
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.subheader("Cleaning Operations")
            
            operation = st.radio("Select Operation:", [
                "Drop Rows with NaN",
                "Drop Columns > 50% NaN",
                "Fill Numeric (Mean)",
                "Fill Numeric (Median)",
                "Fill Numeric (Zero)",
                "Remove Duplicates",
                "Infer Better Dtypes",
                "Remove Outliers (IQR)"
            ])
            
            op_map = {
                "Drop Rows with NaN": "drop_rows_na",
                "Drop Columns > 50% NaN": "drop_cols_na",
                "Fill Numeric (Mean)": "fill_mean",
                "Fill Numeric (Median)": "fill_median",
                "Fill Numeric (Zero)": "fill_zero",
                "Remove Duplicates": "remove_duplicates",
                "Infer Better Dtypes": "infer_dtypes",
                "Remove Outliers (IQR)": "remove_outliers"
            }
            
            if operation == "Remove Outliers (IQR)":
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                col = st.selectbox("Select Column", numeric_cols)
                if st.button("Apply Outlier Removal"):
                    df_cleaned = clean_data(df, op_map[operation], column=col)
                    st.session_state['df'] = df_cleaned
                    df = df_cleaned
                    st.success(f"✅ Removed outliers from {col}")
            else:
                if st.button("Apply Operation"):
                    df_cleaned = clean_data(df, op_map[operation])
                    st.session_state['df'] = df_cleaned
                    df = df_cleaned
                    removed = df.shape[0] - df_cleaned.shape[0]
                    st.success(f"✅ Operation completed!")
                    if removed > 0:
                        st.info(f"Removed {removed} rows")
            
            if st.button("Reset to Original"):
                st.session_state['df'] = st.session_state['df_raw'].copy()
                df = st.session_state['df']
                st.success("✅ Reset to original data")
        
        with col_right:
            st.subheader("Cleaning Log")
            st.info(f"Current dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")
            
            # Missing value heatmap
            st.write("**Missing Values by Column:**")
            missing_data = df.isnull().sum()
            if missing_data.sum() > 0:
                fig, ax = plt.subplots(figsize=(10, 4))
                missing_data.plot(kind='barh', ax=ax, color='coral')
                ax.set_xlabel('Count')
                st.pyplot(fig)
            else:
                st.success("✅ No missing values!")
    
    # ═══════════════════════════════════════════════════════════════
    #  TAB 3: VISUALIZE
    # ═══════════════════════════════════════════════════════════════
    with tab3:
        st.header("Data Visualization")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            chart_type = st.selectbox("Chart Type", [
                "Histogram", "Box Plot", "Violin Plot", "Scatter Plot",
                "Bar Chart", "Line Chart", "KDE Plot", "Count Plot"
            ])
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        with col2:
            x_col = st.selectbox("X Column", numeric_cols + categorical_cols)
        
        with col3:
            y_col = st.selectbox("Y Column", [None] + numeric_cols, help="Optional")
        
        with col4:
            palette = st.selectbox("Palette", [
                "deep", "muted", "bright", "pastel", "dark", "colorblind", "viridis"
            ])
        
        if st.button("Generate Plot"):
            try:
                fig, ax = plt.subplots(figsize=(12, 6))
                
                if chart_type == "Histogram":
                    ax.hist(df[x_col].dropna(), bins=30, color='steelblue', edgecolor='black')
                    ax.set_xlabel(x_col)
                    ax.set_ylabel("Frequency")
                
                elif chart_type == "Box Plot":
                    df.boxplot(column=x_col, ax=ax)
                
                elif chart_type == "Violin Plot":
                    sns.violinplot(data=df, y=x_col, ax=ax, palette=palette)
                
                elif chart_type == "Scatter Plot" and y_col:
                    ax.scatter(df[x_col], df[y_col], alpha=0.6, s=30)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                
                elif chart_type == "Bar Chart":
                    df[x_col].value_counts().head(15).plot(kind='bar', ax=ax, color='steelblue')
                    ax.set_ylabel("Count")
                
                elif chart_type == "KDE Plot":
                    df[x_col].plot(kind='kde', ax=ax, color='steelblue')
                    ax.set_xlabel(x_col)
                
                elif chart_type == "Count Plot":
                    counts = df[x_col].value_counts().head(15)
                    ax.barh(range(len(counts)), counts.values, color='steelblue')
                    ax.set_yticks(range(len(counts)))
                    ax.set_yticklabels(counts.index)
                
                plt.tight_layout()
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error creating plot: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    #  TAB 4: CORRELATION
    # ═══════════════════════════════════════════════════════════════
    with tab4:
        st.header("Correlation Analysis")
        
        numeric_df = df.select_dtypes(include=np.number)
        
        if numeric_df.shape[1] < 2:
            st.warning("⚠️ Need at least 2 numeric columns for correlation analysis.")
        else:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                method = st.selectbox("Correlation Method", ["pearson", "spearman", "kendall"])
            
            with col2:
                pass
            
            corr_matrix = numeric_df.corr(method=method)
            
            # Heatmap
            st.subheader("Correlation Heatmap")
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, ax=ax, cbar_kws={'label': f'{method.capitalize()} Correlation'})
            plt.tight_layout()
            st.pyplot(fig)
            
            # Top correlations
            st.subheader("Top Correlated Pairs")
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    col1_name = corr_matrix.columns[i]
                    col2_name = corr_matrix.columns[j]
                    corr_val = corr_matrix.iloc[i, j]
                    corr_pairs.append({
                        "Column 1": col1_name,
                        "Column 2": col2_name,
                        f"{method.capitalize()} Correlation": corr_val
                    })
            
            pairs_df = pd.DataFrame(corr_pairs).sort_values(
                f"{method.capitalize()} Correlation", key=abs, ascending=False
            )
            st.dataframe(pairs_df.head(10), use_container_width=True)
    
    # ═══════════════════════════════════════════════════════════════
    #  TAB 5: INSIGHTS
    # ═══════════════════════════════════════════════════════════════
    with tab5:
        st.header("Statistical Insights")
        
        if st.button("📊 Generate Statistical Report"):
            insights = generate_stats_report(df)
            for line in insights:
                st.write(line)
        
        st.subheader("Numeric Column Distributions")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            cols = st.columns(2)
            for idx, col in enumerate(numeric_cols[:6]):
                with cols[idx % 2]:
                    fig, ax = plt.subplots(figsize=(6, 3))
                    ax.hist(df[col].dropna(), bins=20, color='steelblue', edgecolor='black')
                    ax.set_title(f"{col} Distribution")
                    ax.set_xlabel(col)
                    ax.set_ylabel("Frequency")
                    st.pyplot(fig)
        
        # Groq AI Chat
        if 'groq_api_key' in st.session_state:
            st.subheader("🤖 Ask Groq AI")
            st.info("Get AI-powered insights about your dataset")
            
            user_question = st.text_area("Ask a question about your data:", height=3)
            
            if st.button("Ask AI"):
                try:
                    from utils.GROQ_client import GroqClient, build_analysis_prompt
                    
                    client = GroqClient(st.session_state['groq_api_key'])
                    
                    # Build prompt with dataset context
                    stats = generate_stats_report(df)
                    context = "\n".join(stats)
                    
                    prompt = f"""You are a data analyst. Here's the dataset summary:\n\n{context}\n\nUser question: {user_question}"""
                    
                    with st.spinner("🤖 Groq is thinking..."):
                        response = client.send_request(
                            prompt=prompt,
                            model="mixtral-8x7b-32768"
                        )
                    
                    st.write("**AI Response:**")
                    st.write(response)
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ═══════════════════════════════════════════════════════════════
    #  TAB 6: EXPORT
    # ═══════════════════════════════════════════════════════════════
    with tab6:
        st.header("Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="data_cleaned.csv",
                mime="text/csv"
            )
        
        with col2:
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            st.download_button(
                label="📥 Download as Excel",
                data=buffer,
                file_name="data_cleaned.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            json_str = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_str,
                file_name="data_cleaned.json",
                mime="application/json"
            )
        
        st.subheader("Export Report")
        
        if st.button("Generate Full Report"):
            report = StringIO()
            report.write("# DataLens Analysis Report\n\n")
            report.write("## Dataset Summary\n")
            insights = generate_stats_report(df)
            for line in insights:
                report.write(line + "\n")
            
            st.download_button(
                label="📥 Download Report as Text",
                data=report.getvalue(),
                file_name="analysis_report.txt",
                mime="text/plain"
            )

else:
    # No file uploaded
    st.title("🎯 DataLens Analytics Dashboard")
    st.markdown("""
    Welcome to **DataLens** — Your web-based data analytics platform!
    
    ### Features:
    - 📊 **Overview**: Dataset statistics and data preview
    - 🧹 **Cleaning**: Remove missing values, duplicates, and outliers
    - 📈 **Visualize**: Create interactive charts (histogram, scatter, box plot, etc.)
    - 🔗 **Correlation**: Analyze relationships between variables
    - 💡 **Insights**: Statistical analysis + Groq AI integration
    - 📤 **Export**: Download cleaned data in CSV, Excel, or JSON
    
    ### Quick Start:
    1. Upload a CSV or Excel file in the sidebar
    2. Explore your data with the available tabs
    3. (Optional) Add your Groq API key for AI insights
    4. Export your cleaned data
    
    **Get your free Groq API key at:** https://console.groq.com
    """)
    
    st.markdown("---")
    st.info("👈 Upload a dataset in the sidebar to begin!")
