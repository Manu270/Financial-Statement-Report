# import os
# import pdfplumber
# import pandas as pd
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# import openai

# # ✅ Set OpenAI API Key
# openai.api_key = "your_openai_api_key_here"

# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = "uploads"
# OUTPUT_FOLDER = "outputs"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# # ✅ Convert PDF to Excel (Improved Stability)
# def pdf_to_excel(pdf_path, excel_path):
#     try:
#         with pdfplumber.open(pdf_path) as pdf:
#             tables = []
#             for page in pdf.pages:
#                 extracted_tables = page.extract_tables()
#                 if extracted_tables:
#                     for table in extracted_tables:
#                         if not table or len(table) < 2:
#                             continue
#                         df = pd.DataFrame(table[1:], columns=table[0])

#                         # ✅ Ensure Unique Column Names
#                         df.columns = [f"{col}_{i}" if col in df.columns[:i] else col for i, col in enumerate(df.columns)]
                        
#                         tables.append(df)

#             if not tables:
#                 return None

#             combined_df = pd.concat(tables, ignore_index=True)
#             combined_df.to_excel(excel_path, index=False, engine='openpyxl')
#             return excel_path

#     except Exception as e:
#         print(f"❌ Error processing PDF: {e}")
#         return None

# # ✅ Upload File API (Handles File Upload)
# @app.route("/upload", methods=["POST"])
# def upload_file():
#     if "file" not in request.files:
#         return jsonify({"error": "No file provided"}), 400

#     file = request.files["file"]
#     filename = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(filename)

#     output_filename = f"{os.path.splitext(file.filename)[0]}.xlsx"
#     output_path = os.path.join(OUTPUT_FOLDER, output_filename)

#     excel_file = pdf_to_excel(filename, output_path)
#     if excel_file:
#         return jsonify({"message": "File processed successfully", "download_url": f"/download/{output_filename}"})
#     else:
#         return jsonify({"error": "Failed to extract data from PDF"}), 500

# # ✅ Download Processed Excel API
# @app.route("/download/<filename>", methods=["GET"])
# def download_file(filename):
#     return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

# # ✅ AI-Powered Financial Analysis (GPT Integration) - Fixed API for OpenAI v1.0+
# @app.route("/ask", methods=["POST"])
# def ai_question():
#     data = request.json
#     question = data.get("question", "").strip()
    
#     if not question:
#         return jsonify({"error": "No question provided"}), 400

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",  # Change to "gpt-4" if available
#             messages=[
#                 {"role": "system", "content": "You are an AI assistant specializing in financial statement analysis."},
#                 {"role": "user", "content": f"{question}"}
#             ],
#             max_tokens=150,
#             temperature=0.7
#         )
        
#         ai_answer = response["choices"][0]["message"]["content"].strip()
#         print(f"✅ AI Response: {ai_answer}")  # Debugging log
#         return jsonify({"answer": ai_answer})

#     except Exception as e:
#         print(f"❌ OpenAI API Error: {e}")
#         return jsonify({"error": "AI service is unavailable."}), 500

# # ✅ Run Flask App
# if __name__ == "__main__":
#     app.run(debug=True)





import os
import pdfplumber
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai

# ✅ Set OpenAI API Key
openai.api_key = "your_openai_api_key_here"

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ Convert PDF to Categorized Excel with Multiple Statements
def pdf_to_excel(pdf_path, excel_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            tables = {}
            current_statement = None
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Detect financial statement types
                if "Consolidated Balance Sheets" in text:
                    current_statement = "Balance Sheet"
                elif "Consolidated Statements of Operations" in text:
                    current_statement = "Income Statement"
                elif "Consolidated Statements of Comprehensive Income" in text:
                    current_statement = "Comprehensive Income"
                elif "Consolidated Statements of Cash Flows" in text:
                    current_statement = "Cash Flow"
                elif "Consolidated Statements of Equity" in text:
                    current_statement = "Equity Statement"
                
                if current_statement:
                    extracted_tables = page.extract_tables()
                    if extracted_tables:
                        for table in extracted_tables:
                            if not table or len(table) < 2:
                                continue
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df.columns = [f"{col}_{i}" if col in df.columns[:i] else col for i, col in enumerate(df.columns)]
                            
                            if current_statement not in tables:
                                tables[current_statement] = []
                            tables[current_statement].append(df)
            
            if not tables:
                return None
            
            # Save categorized data to multiple sheets in Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                for statement, dfs in tables.items():
                    combined_df = pd.concat(dfs, ignore_index=True)
                    
                    # ✅ Add Calculation and Difference Rows
                    total_row = combined_df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').sum()
                    calculation_row = ["Calculation"] + list(total_row)
                    difference_row = ["Difference"] + list(combined_df.iloc[-1, 1:].apply(pd.to_numeric, errors='coerce') - total_row)
                    
                    combined_df.loc[len(combined_df)] = calculation_row
                    combined_df.loc[len(combined_df)] = difference_row
                    
                    combined_df.to_excel(writer, sheet_name=statement, index=False)
            
            return excel_path
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return None

# ✅ Upload File API
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    output_filename = f"{os.path.splitext(file.filename)[0]}.xlsx"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    excel_file = pdf_to_excel(filename, output_path)
    if excel_file:
        return jsonify({"message": "File processed successfully", "download_url": f"/download/{output_filename}"})
    else:
        return jsonify({"error": "Failed to extract data from PDF"}), 500

# ✅ Download Processed Excel API
@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

# ✅ AI-Powered Financial Analysis
@app.route("/ask", methods=["POST"])
def ai_question():
    data = request.json
    question = data.get("question", "").strip()
    
    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant specializing in financial statement analysis."},
                {"role": "user", "content": f"{question}"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        ai_answer = response["choices"][0]["message"]["content"].strip()
        print(f"✅ AI Response: {ai_answer}")
        return jsonify({"answer": ai_answer})

    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return jsonify({"error": "AI service is unavailable."}), 500

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
