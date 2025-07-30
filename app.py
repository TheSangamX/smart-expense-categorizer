import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Import our categorization function
from categorizer import categorize_transaction

# Page configuration
st.set_page_config(
    page_title="Smart Expense Categorizer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">💰 Smart Expense Categorizer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload your transactions and get intelligent categorization with visual insights</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Upload CSV**: Your file should contain 'Date', 'Description', and 'Amount' columns
        2. **Review**: Check the automatically categorized transactions
        3. **Analyze**: View spending patterns in the pie chart
        4. **Download**: Export your categorized data
        """)
        
        st.header("📊 Sample Categories")
        st.markdown("""
        - 🍔 **Food & Dining**
        - 🚗 **Transportation**
        - 🏠 **Utilities**
        - 🛍️ **Shopping**
        - 🎬 **Entertainment**
        - 🏥 **Healthcare**
        - 💰 **Income**
        - 📚 **Education**
        - 🏦 **Banking**
        - ❓ **Others**
        """)
    
    # File upload
    st.header("📁 Upload Your Transaction Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload a CSV file with columns: Date, Description, Amount"
    )
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = ['Date', 'Description', 'Amount']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                st.info("Please ensure your CSV has columns: Date, Description, Amount")
                return
            
            # Convert Date column to datetime
            try:
                df['Date'] = pd.to_datetime(df['Date'])
            except:
                st.error("Unable to parse Date column. Please ensure dates are in a recognizable format.")
                return
            
            # Convert Amount to numeric
            try:
                df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
                df = df.dropna(subset=['Amount'])
            except:
                st.error("Unable to parse Amount column. Please ensure amounts are numeric.")
                return
            
            # Categorize transactions
            st.header("🔄 Processing Transactions...")
            progress_bar = st.progress(0)
            
            categories = []
            for i, description in enumerate(df['Description']):
                category = categorize_transaction(description)
                categories.append(category)
                progress_bar.progress((i + 1) / len(df))
            
            df['Category'] = categories
            progress_bar.empty()
            
            # Display success message
            st.success(f"✅ Successfully processed {len(df)} transactions!")
            
            # KPIs Section
            st.header("📊 Key Performance Indicators")
            
            # Calculate metrics
            total_spending = df[df['Amount'] < 0]['Amount'].sum() * -1  # Convert to positive
            total_income = df[df['Amount'] > 0]['Amount'].sum()
            net_amount = total_income - total_spending
            total_transactions = len(df)
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="💸 Total Spending",
                    value=f"${total_spending:,.2f}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="💰 Total Income",
                    value=f"${total_income:,.2f}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="📈 Net Amount",
                    value=f"${net_amount:,.2f}",
                    delta=None,
                    delta_color="normal" if net_amount >= 0 else "inverse"
                )
            
            with col4:
                st.metric(
                    label="🔢 Total Transactions",
                    value=f"{total_transactions:,}",
                    delta=None
                )
            
            # Category-wise analysis
            st.header("📈 Category Analysis")
            
            # Prepare data for visualization (only expenses)
            expense_df = df[df['Amount'] < 0].copy()
            expense_df['Amount'] = expense_df['Amount'] * -1  # Convert to positive for visualization
            
            if not expense_df.empty:
                category_summary = expense_df.groupby('Category').agg({
                    'Amount': ['sum', 'count'],
                    'Description': 'first'
                }).round(2)
                
                category_summary.columns = ['Total_Amount', 'Transaction_Count', 'Sample_Description']
                category_summary = category_summary.sort_values('Total_Amount', ascending=False)
                
                # Display category summary table
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("💳 Spending by Category")
                    st.dataframe(
                        category_summary[['Total_Amount', 'Transaction_Count']],
                        use_container_width=True
                    )
                
                with col2:
                    st.subheader("🥧 Spending Distribution")
                    
                    # Create pie chart
                    fig = px.pie(
                        values=category_summary['Total_Amount'],
                        names=category_summary.index,
                        title="Spending Distribution by Category",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
                    )
                    
                    fig.update_layout(
                        showlegend=True,
                        height=400,
                        font=dict(size=12)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Display categorized transactions
            st.header("📋 Categorized Transactions")
            
            # Add filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_categories = st.multiselect(
                    "Filter by Category",
                    options=sorted(df['Category'].unique()),
                    default=sorted(df['Category'].unique())
                )
            
            with col2:
                date_range = st.date_input(
                    "Date Range",
                    value=(df['Date'].min().date(), df['Date'].max().date()),
                    min_value=df['Date'].min().date(),
                    max_value=df['Date'].max().date()
                )
            
            with col3:
                amount_filter = st.selectbox(
                    "Amount Filter",
                    options=["All", "Income Only", "Expenses Only"],
                    index=0
                )
            
            # Apply filters
            filtered_df = df[df['Category'].isin(selected_categories)]
            
            if len(date_range) == 2:
                filtered_df = filtered_df[
                    (filtered_df['Date'].dt.date >= date_range[0]) &
                    (filtered_df['Date'].dt.date <= date_range[1])
                ]
            
            if amount_filter == "Income Only":
                filtered_df = filtered_df[filtered_df['Amount'] > 0]
            elif amount_filter == "Expenses Only":
                filtered_df = filtered_df[filtered_df['Amount'] < 0]
            
            # Display filtered data
            st.dataframe(
                filtered_df.sort_values('Date', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Download section
            st.header("💾 Download Categorized Data")
            
            # Prepare download data
            download_df = df.copy()
            download_df['Date'] = download_df['Date'].dt.strftime('%Y-%m-%d')
            
            # Convert to CSV
            csv_buffer = io.StringIO()
            download_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            # Download button
            st.download_button(
                label="📥 Download Categorized CSV",
                data=csv_data,
                file_name=f"categorized_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download your transactions with categories added"
            )
            
        except Exception as e:
            st.error(f"An error occurred while processing your file: {str(e)}")
            st.info("Please check your file format and try again.")
    
    else:
        # Show sample data format
        st.header("📋 Sample Data Format")
        st.info("Upload a CSV file to get started, or see the sample format below:")
        
        sample_data = {
            'Date': ['2024-01-15', '2024-01-16', '2024-01-17'],
            'Description': ['Starbucks Coffee', 'Salary Deposit', 'Uber Ride'],
            'Amount': [-5.50, 3000.00, -12.30]
        }
        
        sample_df = pd.DataFrame(sample_data)
        st.dataframe(sample_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()