# Natural-Language-to-SQL-
**NATURAL LANGUAGE TO SQL CONVERTER USING LLM**

*This project is a Streamlit-based web app that allows users to upload structured data files (CSV, Excel, PDF, Word) and query them using natural language. The app uses Google Gemini 1.5 Pro via the Generative AI API to convert plain English queries into SQL statements.*

**Features**
*Upload support for: .csv, .xlsx, .pdf, .docx

*Uses Google Gemini for converting English to SQL

*Interactive query generation and execution

*Temporary SQLite database from uploaded files

*Animated UI with dark mode and neon-themed style

*Displays raw SQL and execution results

*Cleans up temporary files after execution

**Component**	                              **Description**
Frontend	                                    Streamlit for building UI
LLM	                                       Google Gemini 1.5 Pro
Database	                                    SQLite3
PDF Extraction	                              PyMuPDF (fitz)
DOCX Extraction	                           python-docx
Environment Config	                        python-dotenv

🧪 **How It Works**
-User uploads a file (CSV, Excel, PDF, DOCX).
-The file is parsed into a Pandas DataFrame.
-The data is saved into a temporary SQLite DB (uploaded_data.db).
-User enters a natural language query.
-Gemini API translates it into SQL.
-SQL is executed on the SQLite database.
-Results are displayed in the app.
-Temporary DB is deleted after execution.

❤️**Contributors**
Komal Sharma
Ishika Panwar
