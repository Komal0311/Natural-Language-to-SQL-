import os
import sqlite3
import pandas as pd
import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import docx
from dotenv import load_dotenv
from io import BytesIO

# Set the page config as the first Streamlit command
st.set_page_config(page_title="Universal SQL Generator", layout="centered")

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Check if the API key is being loaded correctly
if not API_KEY:
    st.error("Google API Key is missing. Please check your .env file.")
    st.stop()
else:
    st.success("API Key Loaded Successfully!")

# Configure the Gemini API
genai.configure(api_key=API_KEY)

# Dark mode + pink-themed style for the Streamlit app
def set_dark_background():
    css = """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #FFFFFF;
        font-family: 'Segoe UI', sans-serif;
    }
    header, footer {
        background-color: #000000 !important;
    }
    [data-testid="stHeader"] {
        background: #000000;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
        box-shadow: 0 2px 10px rgba(255, 110, 196, 0.4);
    }
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"],
    .stDeployButton,
    [data-testid="stMenu"] {
        background-color: #ff6ec4 !important;
        color: white !important;
        border-radius: 10px;
        padding: 4px 8px;
        box-shadow: 0 0 10px #ff6ec4;
    }
    .stTextInput>div>div>input {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #ff6ec4;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button {
        background: linear-gradient(to right, #ff6ec4, #7873f5);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 0.6em 1.2em;
        box-shadow: 0 0 10px #ff6ec4;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #66a6ff, #aaf0ff);
        box-shadow: 0 0 20px #66a6ff;
        color: black;
    }
    .stDataFrame, .stCode {
        background-color: #1a1a1a;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 0 10px #7873f5;
    }
    .stAlert {
        background-color: #222222;
        color: #ff6ec4;
        border-radius: 8px;
    }
    hr {
        border: 1px solid #66a6ff;
        margin: 1.5rem 0;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# App config and style
set_dark_background()

# Animated heading
st.markdown("""
<h1 style='
    text-align: center;
    font-size: 3em;
    font-weight: 800;
    background: linear-gradient(90deg, #ff6ec4, #7873f5, #66a6ff);
    background-size: 200% auto;
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s linear infinite;
'>
✨ Natural Language to SQL Converter
</h1>
<style>
@keyframes shine {
  to {
    background-position: 200% center;
  }
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h4>📂 Upload a File or Use Sample Student DB</h4>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload CSV, Excel, PDF, or Word file", type=["csv", "xlsx", "pdf", "docx"])

# Gemini call function with error handling
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content([prompt[0], question])
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini Error: {e}")
        st.write(f"Error details: {e}")
        return None

# SQLite execution with error handling
def execute_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        if sql.strip().lower().startswith("select"):
            rows = cur.fetchall()
            conn.close()
            return rows, "select"
        else:
            conn.commit()
            conn.close()
            return None, "action"
    except sqlite3.Error as e:
        st.error(f"SQL Execution Error: {e}")
        return None, "error"

# File extract (supports CSV, Excel, PDF, DOCX)
def extract_table(file, filetype):
    try:
        if filetype == "csv":
            return pd.read_csv(file)
        elif filetype == "xlsx":
            return pd.read_excel(file)
        elif filetype == "pdf":
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text = "".join(page.get_text() for page in doc)
            df = pd.read_fwf(BytesIO(text.encode()))
            return df
        elif filetype == "docx":
            doc = docx.Document(file)
            data = [[cell.text for cell in row.cells] for table in doc.tables for row in table.rows]
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        else:
            st.error("Unsupported file type.")
            return None
    except Exception as e:
        st.error(f"File Processing Error: {e}")
        return None

# Save dataframe to SQLite
def dataframe_to_sqlite(df, db_name):
    try:
        conn = sqlite3.connect(db_name)
        df.to_sql('UPLOADED_DATA', conn, if_exists='replace', index=False)
        conn.close()
        return df.columns.tolist()
    except Exception as e:
        st.error(f"SQLite Save Error: {e}")
        return []

# Load file or sample
db_name = "student.db"
table = "STUDENT"
columns = ["NAME", "CLASS", "SECTION", "MARKS"]

if uploaded_file:
    filetype = uploaded_file.name.split('.')[-1]
    with st.spinner("🔄 Extracting data..."):
        df = extract_table(uploaded_file, filetype)
        if df is not None:
            st.success("✅ File uploaded successfully!")
            st.dataframe(df)
            db_name = "uploaded_data.db"
            columns = dataframe_to_sqlite(df, db_name)
            table = "UPLOADED_DATA"
        else:
            st.stop()

# Gemini prompt
prompt = [f"""
You are an expert in converting English instructions to valid SQL statements.
The database table is `{table}` and it has the following columns: {', '.join(columns)}.

Guidelines:
- You may generate SELECT, INSERT, UPDATE, or DELETE statements.
- Do not create, drop or alter tables.
- Return only the SQL code, no explanations.
- No backticks or extra formatting.
"""]

# Input for natural language query
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("🧬 Ask a Question in Plain English")

question = st.text_input("E.g., 'Show all students scoring above 90'", key="user_input")
submit = st.button("✨ Generate & Run SQL")

# Query execution
if submit:
    with st.spinner("⚙️ Generating and executing SQL..."):
        response = get_gemini_response(question, prompt)
        if response:
            st.subheader("💻 Generated SQL:")
            st.code(response, language='sql')
            result, action = execute_sql_query(response, db_name)

            if action == "select":
                st.subheader("📊 Query Results")
                if result:
                    st.dataframe(result)
                else:
                    st.info("No results found.")
            elif action == "action":
                st.success("✅ SQL command executed successfully.")
            else:
                st.error("Execution failed.")

    # Clean up after execution
    if uploaded_file:
        os.remove(db_name)
        st.info("🗑️ Temporary database deleted.")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<center>🚀 Made with ❤️ by <b style='color:#ff6ec4;'>Komal & Ishika</b></center>", unsafe_allow_html=True)
