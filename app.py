# import os
# import pdfplumber
# import pandas as pd
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# import google.generativeai as genai
# import re

# # ✅ Set Gemini API Key
# genai.configure(api_key="AIzaSyCWJ-hXKmlCaUIFFuEYK8EfljjpyeDAclc")
# generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 64,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain",
# }
# model = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     generation_config=generation_config,
# )

# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = "uploads"
# OUTPUT_FOLDER = "outputs"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# # ✅ Convert PDF to Categorized Excel with Multiple Statements
# def pdf_to_excel(pdf_path, output_folder):
#     try:
#         output_filename = f"{os.path.splitext(os.path.basename(pdf_path))[0]}.xlsx"
#         excel_path = os.path.join(output_folder, output_filename)
        
#         with pdfplumber.open(pdf_path) as pdf:
#             tables = {}
#             current_statement = None
#             for page in pdf.pages:
#                 text = page.extract_text()
#                 if not text:
#                     continue
                
#                 # Detect financial statement types
#                 if "Consolidated Balance Sheets" in text:
#                     current_statement = "Balance Sheet"
#                 elif "Consolidated Statements of Operations" in text:
#                     current_statement = "Income Statement"
#                 elif "Consolidated Statements of Comprehensive Income" in text:
#                     current_statement = "Comprehensive Income"
#                 elif "Consolidated Statements of Cash Flows" in text:
#                     current_statement = "Cash Flow"
#                 elif "Consolidated Statements of Equity" in text:
#                     current_statement = "Equity Statement"
                
#                 if current_statement:
#                     extracted_tables = page.extract_tables()
#                     if extracted_tables:
#                         for table in extracted_tables:
#                             if not table or len(table) < 2:
#                                 continue
#                             df = pd.DataFrame(table[1:], columns=table[0])
#                             df.columns = [f"{col}_{i}" if col in df.columns[:i] else col for i, col in enumerate(df.columns)]
                            
#                             # ✅ Remove Dollar Symbols & Handle Missing Values
#                             df = df.map(lambda x: re.sub(r'\$', '', str(x)) if isinstance(x, str) else x)
#                             df.fillna("", inplace=True)
                            
#                             if current_statement not in tables:
#                                 tables[current_statement] = []
#                             tables[current_statement].append(df)
            
#             if not tables:
#                 return None
            
#             # Save categorized data to multiple sheets in Excel
#             with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
#                 for statement, dfs in tables.items():
#                     combined_df = pd.concat(dfs, ignore_index=True)
                    
#                     # ✅ Automatically Detect & Add Calculation Rows with Formulas
#                     numeric_cols = combined_df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
#                     total_row = numeric_cols.sum()
#                     calculation_row = ["Calculation"] + [f"=SUM(B2:B{len(combined_df)})"] * (len(numeric_cols.columns))
#                     difference_row = ["Difference"] + [f"=B{len(combined_df)+1}-B{len(combined_df)}"] * (len(numeric_cols.columns))
                    
#                     combined_df.loc[len(combined_df)] = calculation_row
#                     combined_df.loc[len(combined_df)] = difference_row
                    
#                     combined_df.to_excel(writer, sheet_name=statement, index=False)
            
#             return excel_path
#     except Exception as e:
#         print(f"❌ Error processing PDF: {e}")
#         return None

# # ✅ Upload File API
# @app.route("/upload", methods=["POST"])
# def upload_file():
#     if "file" not in request.files:
#         return jsonify({"error": "No file provided"}), 400

#     file = request.files["file"]
#     filename = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(filename)

#     excel_file = pdf_to_excel(filename, OUTPUT_FOLDER)
#     if excel_file:
#         return jsonify({"message": "File processed successfully", "download_url": f"/download/{os.path.basename(excel_file)}"})
#     else:
#         return jsonify({"error": "Failed to extract data from PDF"}), 500

# # ✅ Download Processed Excel API
# @app.route("/download/<filename>", methods=["GET"])
# def download_file(filename):
#     return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

# # ✅ AI-Powered Financial Analysis
# @app.route("/ask", methods=["POST"])
# def ai_question():
#     data = request.json
#     question = data.get("question", "").strip()
    
#     if not question:
#         return jsonify({"error": "No question provided"}), 400

#     try:
#         chat_session = model.start_chat(history=[])
#         response = chat_session.send_message(question)
#         ai_answer = response.text
#         print(f"✅ AI Response: {ai_answer}")
#         return jsonify({"answer": ai_answer})

#     except Exception as e:
#         print(f"❌ Gemini API Error: {e}")
#         return jsonify({"error": "AI service is unavailable."}), 500

# # ✅ Run Flask App
# if __name__ == "__main__":
#     app.run(debug=True)




import os
import pdfplumber
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import re

# ✅ Set Gemini API Key
genai.configure(api_key="AIzaSyCWJ-hXKmlCaUIFFuEYK8EfljjpyeDAclc")
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ Convert PDF to Categorized Excel with Multiple Statements
def pdf_to_excel(pdf_path, output_folder):
    try:
        output_filename = f"{os.path.splitext(os.path.basename(pdf_path))[0]}.xlsx"
        excel_path = os.path.join(output_folder, output_filename)
        
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
                            
                            # ✅ Remove Dollar Symbols & Handle Missing Values
                            df = df.map(lambda x: re.sub(r'\$', '', str(x)) if isinstance(x, str) else x)
                            df.fillna("", inplace=True)
                            
                            if current_statement not in tables:
                                tables[current_statement] = []
                            tables[current_statement].append(df)
            
            if not tables:
                return None
            
            # Save categorized data to multiple sheets in Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                for statement, dfs in tables.items():
                    combined_df = pd.concat(dfs, ignore_index=True)
                    
                    # ✅ Automatically Detect & Add Calculation Rows with Formulas
                    numeric_cols = combined_df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
                    total_row = numeric_cols.sum()
                    calculation_row = ["Calculation"] + [f"=SUM(B2:B{len(combined_df)})"] * (len(numeric_cols.columns))
                    difference_row = ["Difference"] + [f"=B{len(combined_df)+1}-B{len(combined_df)}"] * (len(numeric_cols.columns))
                    
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

    excel_file = pdf_to_excel(filename, OUTPUT_FOLDER)
    if excel_file:
        return jsonify({"message": "File processed successfully", "download_url": f"/download/{os.path.basename(excel_file)}"})
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
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(question)
        ai_answer = response.text
        print(f"✅ AI Response: {ai_answer}")
        return jsonify({"answer": ai_answer})

    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return jsonify({"error": "AI service is unavailable."}), 500

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)

