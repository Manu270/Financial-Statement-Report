import streamlit as st
import pdfplumber
import pandas as pd
import openai
import os

# Set your OpenAI API key
openai.api_key = "your_openai_api_key_here"

# Function to extract tables from PDF
def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            for table in extracted_tables:
                df = pd.DataFrame(table)
                tables.append(df)
    return tables

# Function to process financial statement and perform recalculations
def process_financial_statement(pdf_path, output_path):
    tables = extract_tables_from_pdf(pdf_path)
    
    if not tables:
        st.error("No tables found in the provided PDF.")
        return None
    
    # Combine all extracted tables
    financial_data = pd.concat(tables, ignore_index=True)

    # Identify total rows and perform recalculations
    financial_data.fillna("", inplace=True)
    financial_data.columns = financial_data.iloc[0]  # Set header row
    financial_data = financial_data[1:]  # Remove header row

    # Add recalculation and difference rows
    for index, row in financial_data.iterrows():
        if "Total" in str(row[0]):  # Detect total/subtotal rows
            calculated_value = pd.to_numeric(financial_data.iloc[index - 1, 1:], errors='coerce').sum()
            actual_value = pd.to_numeric(row[1:], errors='coerce').sum()

            financial_data.loc[index + 1] = ["Calculation"] + list(calculated_value)
            financial_data.loc[index + 2] = ["Difference"] + list(calculated_value - actual_value)

    # Save to Excel
    financial_data.to_excel(output_path, index=False)
    return output_path

# Function for AI-powered Q&A system
def ask_financial_ai(question, financial_data):
    context = f"Here is a financial statement data:\n{financial_data.to_string()}\n\n"
    prompt = f"{context}Based on this data, {question}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a financial analyst assistant."},
                  {"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("AI-Based Financial Statement Analyzer")

uploaded_file = st.file_uploader("Upload 10-K Financial Report (PDF)", type=["pdf"])

if uploaded_file:
    input_pdf_path = f"temp_{uploaded_file.name}"
    output_excel_path = "output.xlsx"

    with open(input_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("Processing document...")

    processed_file = process_financial_statement(input_pdf_path, output_excel_path)

    if processed_file:
        st.success("Processing complete! Download your Excel file below.")
        st.download_button(label="Download Excel File", data=open(processed_file, "rb"), file_name="financial_statement.xlsx")

    # AI-based Q&A
    st.header("Ask AI about the Financial Statement")
    user_query = st.text_input("Enter your question (e.g., What is the Total Assets value?)")

    if user_query:
        extracted_data = pd.read_excel(processed_file)
        answer = ask_financial_ai(user_query, extracted_data)
        st.write("AI Response:", answer)
