# 📌 Necessary Imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO

# 🌟 Set Up Streamlit App
st.set_page_config(page_title="Data Sweeper", layout='wide')
st.title("Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# 📂 File Uploader
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

# 🛠️ File Processing
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # 🗂️ Read File as DataFrame
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            try:
                df = pd.read_excel(file, engine="openpyxl")  # ✅ Use openpyxl for xlsx
            except ImportError:
                try:
                    df = pd.read_excel(file, engine="xlsxwriter")  # ✅ Alternative if openpyxl is missing
                except Exception as e:
                    st.error(f"Error loading {file.name}: {e}")
                    continue
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # 📌 File Information
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.getbuffer().nbytes / 1024:.2f} KB")

        # 📊 Data Preview
        st.write("📌 **Preview of the Data:**")
        st.dataframe(df.head())

        # ✨ Data Cleaning Options
        st.subheader("🧹 Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}", key=f"dup_{file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}", key=f"fill_{file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing Values Filled!")

        # 🎯 Select Specific Columns
        st.subheader("📌 Select Columns to Convert")
        selected_columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns, key=f"cols_{file.name}")
        df = df[selected_columns]

        # 📊 Data Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}", key=f"viz_{file.name}"):
            numeric_df = df.select_dtypes(include='number')
            if len(numeric_df.columns) >= 2:
                st.bar_chart(numeric_df.iloc[:, :2])
            else:
                st.warning("⚠️ Not enough numerical columns for visualization.")

        # 🔄 File Conversion Options
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"convert_{file.name}")

        if st.button(f"Convert {file.name}", key=f"convert_btn_{file.name}"):
            buffer = BytesIO()

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            # 📥 File Download Button
            st.download_button(
                label=f"Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

    st.success("✅ All files processed successfully!")
