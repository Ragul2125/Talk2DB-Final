import os
import sqlite3
import snowflake.connector
import openai
from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
from contextlib import closing
from pandasai import SmartDataframe
import pandas as pd
import matplotlib.pyplot as plt
from langchain_community.chat_models import ChatOpenAI
import os
import base64
import io
import logging
from flask_cors import CORS 
import matplotlib
from datetime import datetime, timedelta
import google.generativeai as genai
import regex as re
import pymysql
import certifi
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

matplotlib.use('Agg')  # Prevents GUI errors

# MYSQL_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "root123",  # Replace with your password
#     "database": "talk2db",   # Replace with your DB
#     "charset": "utf8mb4"
#     }

SCHEMA=None
MYSQL_CONFIG = {
    "host": None,
    "user": None,
    "password": None,  # Replace with your password
    "database": None,   # Replace with your DB
    "charset": "utf8mb4"
    }


# Load environment variables
load_dotenv()
genai.configure(api_key='AIzaSyDQvFBvNAdTV3fCv2QLV45T-2w-pRwVDwE')
app = Flask(__name__)
CORS(app)




MONGO_URI = "mongodb+srv://04naveenk:qssJVqm1hPutgmBR@testing.867ct39.mongodb.net/"


try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    # Ping the server to check the connection
    client.admin.command('ping')
    print("✅ Database connected successfully")
except Exception as e:
    print("❌ Failed to connect to the database:", e)

db = client["auth_db"]
users_collection = db["users"]


matplotlib.use('Agg')


# === Mongo Signup ===
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    print(data)
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password
    })

    return jsonify({'message': 'User created successfully'}), 201



# === Mongo Login ===
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    return jsonify({
        'message': 'Login successful',
        'user': {'name': user['name'], 'email': user['email']}
    }), 200


@app.route('/connectdb', methods=['POST'])
def connectdb():
    data = request.json
    user = data.get('user')
    password = data.get('password')
    database = data.get('database')
    

    global MYSQL_CONFIG
    MYSQL_CONFIG = {
    "host": "localhost",
    "user": user,
    "password": password,  # Replace with your password
    "database": database,   # Replace with your DB
    "charset": "utf8mb4"
    }
    
    try:
        conn=pymysql.connect(**MYSQL_CONFIG)
    except Exception as e:
        logging.error(f"MySQL connection error: {e}")
    
    cursor=conn.cursor()

    query="""
SELECT 
    CONCAT(
        t.TABLE_NAME, ' (',
        GROUP_CONCAT(
            CONCAT(
                c.COLUMN_NAME, ' ',
                CASE 
                    WHEN c.DATA_TYPE IN ('int', 'bigint', 'decimal', 'float', 'double') THEN 'NUMBER'
                    WHEN c.DATA_TYPE IN ('varchar', 'text', 'char', 'longtext', 'mediumtext', 'tinytext') THEN 'TEXT'
                    WHEN c.DATA_TYPE IN ('datetime', 'timestamp') THEN 'TIMESTAMP_NTZ'
                    WHEN c.DATA_TYPE = 'date' THEN 'DATE'
                    WHEN c.DATA_TYPE = 'tinyint' AND c.COLUMN_TYPE = 'tinyint(1)' THEN 'BOOLEAN'
                    ELSE UPPER(c.DATA_TYPE)
                END
            )
            ORDER BY c.ORDINAL_POSITION
            SEPARATOR ','
        ),
        ')'
    ) AS schema_string
FROM information_schema.COLUMNS c
JOIN information_schema.TABLES t 
    ON c.TABLE_NAME = t.TABLE_NAME AND t.TABLE_SCHEMA = 'talk2db'
WHERE c.TABLE_SCHEMA = 'talk2db'
GROUP BY t.TABLE_NAME
ORDER BY t.TABLE_NAME;

"""
    global SCHEMA
    SCHEMA=cursor.execute(query)
    
    return MYSQL_CONFIG





llm = genai.GenerativeModel(model_name="gemini-2.0-flash")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")



# Define your system prompt
system_prompt = """
INSTRUCTIONS: Your purpose is to Analyze the database schema and generate the SQL query accordingly. If asked any non-related question, do not generate an SQL query and respond accordingly.
- ONLY RETURN THE RAW SQL QUERY NOT ADD ANY FORMATTING ,MARKDOWN CODE BLOCKS OR SQL TAGES AROUND THE SQL QUERY. DO NOT INCLUDE ANY EXPLANATIONS, MARKDOWN BACKTICKS, OR ADDITIONAL TEXT .
- Ensure the query ends with a semicolon (;).
- Optimize performance by minimizing unnecessary operations.
- Use IN, ON, BY operators as per applicable conditions and subqueries.
- If a query involves multiple steps or conditions, consider breaking it into subqueries or using CTEs.
- SCHEMA-RESTRICTED QUERIES: Only use tables and columns that exist in the schema.
- Return an error if a requested table or column is not found.
- MONTH HANDLING: Use numerical values for months instead of LIKE %pattern%.
- FOR STRING HANDLING: Convert strings to lowercase and use LIKE %pattern% for matching.
- JOIN REQUESTS: Interpret "along" as a request to join tables using valid schema relationships.
- VALIDATION: If a table or column does not exist, diagnose the error and then give me possible issue and return issue do not use the word "Error"
- USER QUERY CHECK:When the user asks a question, check if the question is related to the schema.
- SQL INJECTION: IF user use any sql injection queries return "Permission denied"
- QUERY VALIDATION: Validate the query to ensure it is syntactically correct.
- DATABASE EXPLANATION: If the user wants to know about the database give a simple easy to understand explanation based on the provided schema.
- QUERY RELEVANCE: when the user's specified table or any other value is not available in the provided schema answer with a query which most likely captures the intent of the user.
- ABOUT DATABASE: This is a supermarket database where all tables are linked. If the user does not mention a table name in their query, intelligently determine the most relevant table(s) based on the context before generating the SQL query.
- SCHEMA: Do not assume any tables or schemas on your own , just make the query based on the schema given to you.
- OUTPUT: I need the output text to contain only the raw sql query, which should be directly executable in snowflake database.

Database Schema:
Database name:TALK2DB
{SCHEMA}
EXAMPLE
User: provide me the database name
AI: SELECT DATABASE();
User: list the tables in our database
AI: SHOW TABLES;
"""



# SNOWFLAKE_CONFIG = {
#     "user": 'naveen',
#     "password": 'Naveen@04102005',
#     "account": 'kbvpier-li30198',  
#     "warehouse": 'COMPUTE_WH',
#     "database": 'MEC',
#     "schema": 'SALES',
# }

# === MySQL Config ===
# MYSQL_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "root123",  # Replace with your password
#     "database": "talk2db",   # Replace with your DB
#     "charset": "utf8mb4"
# }


def init_db():
    with closing(sqlite3.connect("database.db")) as conn, closing(conn.cursor()) as cursor:
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                timestamp TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT,
                content TEXT,
                type_of_query TEXT,
                timestamp TEXT,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
        ''')
        conn.commit()






# # Snowflake connection management
# def get_snowflake_connection():
#     try:
#         return snowflake.connector.connect(**SNOWFLAKE_CONFIG)
#     except snowflake.connector.errors.Error as e:
#         logging.error(f"Snowflake connection error: {e}")
#         return None
# === MySQL Connection ===
def get_mysql_connection():
    try:
        return pymysql.connect(**MYSQL_CONFIG)
    except Exception as e:
        logging.error(f"MySQL connection error: {e}")
        return None






# def execute_snowflake_query(query,row=None):
#     conn = get_snowflake_connection()
   
#     if not conn:
#         return {"error": "Failed to connect to Snowflake."}, 500

#     try:
#         with conn.cursor() as cursor:
#             cursor.execute(query)
#             columns = [desc[0] for desc in cursor.description]  # Extract column names
#             if row:
#                 results = cursor.fetchall()[:row]
#             else:
#                 results = cursor.fetchall()
#             # Convert results into list of dictionaries (column_name -> value)
#             formatted_results = [dict(zip(columns, row)) for row in results]

#             return {"results": formatted_results}
#     except snowflake.connector.errors.ProgrammingError as e:
#         logging.error(f"Snowflake query error: {e}")
#         return {"error": "Invalid SQL query."}, 400
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#         return {"error": "An unexpected error occurred."}, 500
#     finally:
#         conn.close()

def execute_mysql_query(query, row=None):
    conn = get_mysql_connection()  # Ensure you have the get_mysql_connection() function from previous code

    if not conn:
        return {"error": "Failed to connect to MySQL."}, 500

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            if row:
                results = cursor.fetchall()[:row]
            else:
                results = cursor.fetchall()
            formatted_results = [dict(zip(columns, r)) for r in results]

            return {"results": formatted_results}
    except pymysql.err.ProgrammingError as e:
        logging.error(f"MySQL query error: {e}")
        return {"error": "Invalid SQL query."}, 400
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"error": "An unexpected error occurred."}, 500
    finally:
        conn.close()






def save_message(conversation_id, role, content,type="system"):
    try:
        with closing(sqlite3.connect("database.db")) as conn, closing(conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content, timestamp,type_of_query)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),type))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")






@app.route("/start_conversation", methods=["POST"])
def start_conversation():
    try:
        with closing(sqlite3.connect("database.db")) as conn, closing(conn.cursor()) as cursor:
            cursor.execute("INSERT INTO conversations (title, timestamp) VALUES (?, ?)",
                           (request.json.get("title", "New Conversation"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conversation_id = cursor.lastrowid
            conn.commit()
            return jsonify({"conversation_id": conversation_id})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500





@app.route("/conversation_history", methods=["GET"])
def get_conversation_history():
    try:
        num_weeks = int(request.args.get("weeks", 5))  # Default to last 5 weeks
        today = datetime.today()
        start_of_this_week = today - timedelta(days=today.weekday())

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            
            # Fetch all conversations within the last N weeks
            min_date = start_of_this_week - timedelta(weeks=num_weeks)
            query = """
                SELECT id, title, timestamp FROM conversations
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """
            cursor.execute(query, (min_date.strftime("%Y-%m-%d"),))
            rows = cursor.fetchall()

            history_list = []
            week_mapping = {}

            for conv_id, title, timestamp in rows:
                conv_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                
                for i in range(num_weeks):
                    week_start = start_of_this_week - timedelta(weeks=i)
                    week_end = week_start + timedelta(days=7)
                    
                    if week_start <= conv_date < week_end:
                        week_label = "This week" if i == 0 else f"{i} weeks ago"
                        
                        if week_label not in week_mapping:
                            week_mapping[week_label] = []
                        
                        week_mapping[week_label].append({"history": title, "id": conv_id})
                        break  # Stop checking after finding the correct week

            for week, historys in week_mapping.items():
                history_list.append({"title": week, "historys": historys})

            return jsonify(history_list)

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500





@app.route("/generate_sql", methods=["POST"])
def generate_sql():
    conversation_id = request.json.get("conversation_id")
    user_query = request.json.get("query")

    if not conversation_id:
        # Create a new conversation if no conversation_id is provided
        with closing(sqlite3.connect("database.db")) as conn, closing(conn.cursor()) as cursor:
            cursor.execute("INSERT INTO conversations (title, timestamp) VALUES (?, ?)",
                           (str(user_query.split(" ")[:2][0]+ " " +user_query.split(" ")[:2][1]) if len(user_query.split(" "))>2 else user_query, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conversation_id = cursor.lastrowid
            conn.commit()

    # Retrieve past conversation messages
    messages = get_conversation1(conversation_id)

    # If no previous messages, start with system message
    if not messages:
        save_message(conversation_id, "system", system_prompt, "system")
        messages = get_conversation1(conversation_id)

    # Append user query
    save_message(conversation_id, "user", user_query, "query")
    messages.append({"role": "user", "content": user_query})

    try:
        # Convert message list to Gemini format
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "system":
                gemini_messages.append(system_prompt)
            else:
                gemini_messages.append(msg["content"])

        model = genai.GenerativeModel("gemini-2.0-flash")
        gen_config=genai.GenerationConfig( temperature=0.25)  # Set your desired temperature value (e.g., 0.0 to 1.0)
        response = model.generate_content(gemini_messages,generation_config=gen_config)
        #look at the generated response to debug
        print("gemini response:",response)

        sql_query = response.text.strip().split("\n\n")[0]
        # check the final query which is sent to the database
        
        if '```' in sql_query:
            sql_query = re.sub(r"```sql\s*|```", "", sql_query, flags=re.IGNORECASE).strip()


        print('final sql query:', sql_query)
        query_type = "query" if sql_query.lower().startswith(("select", "show", "with",)) else "message"
        save_message(conversation_id, "system", sql_query, query_type)

        return jsonify({"conversation_id": conversation_id, "sql": sql_query})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def get_conversation1(conversation_id):
    """Retrieve messages from the database and format them correctly for OpenAI API."""
    try:
        with closing(sqlite3.connect("database.db")) as conn, closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id
            """, (conversation_id,))
            messages = cursor.fetchall()
        
        # Convert tuples into a list of dicts
        formatted_messages = [{"role": row[0], "content": row[1]} for row in messages]

        return formatted_messages  # ✅ Correctly formatted for OpenAI
    except sqlite3.Error:
        return []







@app.route("/execute_query", methods=["POST"])
def execute_query():
    sql_query = request.json.get("query")
    row = request.json.get("row_count")
    print(sql_query)
    if not (sql_query.lower().startswith("select") or sql_query.lower().startswith("show") or sql_query.lower().startswith("with")):
        return jsonify({"error": "Only SELECT queries are allowed."}), 400
    response = execute_mysql_query(sql_query,row)  # Execute query
    return jsonify(response)








@app.route("/conversation/<int:id>", methods=["GET"])
def get_conversation(id):
    try:
        with closing(sqlite3.connect("database.db")) as conn, closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT id, role, content, timestamp, type_of_query 
                FROM messages 
                WHERE conversation_id = ? AND type_of_query != 'system' 
                ORDER BY id
            """, (id,))
            
            messages = []
            for row in cursor.fetchall():
                msg_id, role, content, timestamp, type_of_query = row
                
                if role == "system":
                    messages.append({
                        "id": msg_id,
                        "query": content,
                        "sender": "bot",
                        "responseType": type_of_query
                    })
                else:
                    messages.append({
                        "id": msg_id,
                        "text": content,
                        "sender": "user"
                    })
        
        return jsonify(messages)
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
















# @app.route("/generate_chart", methods=["POST"])
# def generate_chart():
#     """ Handle chart generation request with error handling """
#     try:
#         # Parse JSON input safely
#         data = request.get_json(force=True, silent=True)
#         if not data:
#             return jsonify({"error": "Invalid or missing JSON payload"}), 400

#         chart_type = data.get("chart_type", "bar")
#         num_rows = data.get("num_rows", "All")
#         query1 = data.get("query")
#         table=execute_mysql_query(query1)
        
#         if not isinstance(table["results"], list) or len(table) == 0:
#             return jsonify({"error": "Table data is missing or not in correct format"}), 400

#         print(f"Received data: {data}, num_rows type: {type(num_rows)}")

#         # Convert table data to DataFrame
#         df = pd.DataFrame(table["results"])
#         print(df)
#         row_count = len(df)

#         # Validate row count for certain chart types
#         if isinstance(num_rows, str) and num_rows.lower() == "all":
#             if row_count > 50 and chart_type in ["Histogram", "Bar Chart", "Line Chart", "Pie Chart"]:
#                 return jsonify({"warning": f"{chart_type} cannot display more than 50 rows. Your dataset has {row_count} rows."}), 200

#         # Generate the prompt for AI-based chart generation
#         ques = f"Create a {chart_type} using {'all rows' if num_rows.lower() == 'all' else f'the {num_rows} rows'} of the dataset, analyse the data and put a chart which completes the colour scheme Hexcode:200695, if more colors are needed to better visualize choose colors that compliment the provided hexcode. When mapping labels make sure that the chart produced is meaningful and easy to understand."       
#         print(ques)
#         # AI-Based Smart DataFrame Processing
#         df = SmartDataframe(df, config={"llm": llm})

#         try:
#             result = df.chat(ques)
#         except Exception as ai_error:
#             return jsonify({"error": f"AI processing failed: {str(ai_error)}"}), 500

#         encoded_image = None

#         if isinstance(result, str):
#             if os.path.isfile(result):  # Check if result is a valid file path
#                 print(result)
#                 with open(result, "rb") as image_file:
#                     encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
#         elif isinstance(result, plt.Figure):
#             buf = io.BytesIO()
#             result.savefig(buf, format="png")
#             buf.seek(0)
#             encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")

#         if not encoded_image:
#             return jsonify({"error": "Unsupported response type."}), 500

#         return jsonify({"status": "success", "image": encoded_image})

#     except Exception as e:
#         return jsonify({"error": f"Server error: {str(e)}"}), 500

import webbrowser
import traceback
import random

class SmartDataframe:
    def __init__(self, df, config=None):
        self.df = df

    def chat(self, prompt, chart_type):
        print("🧠 Prompt to SmartDataframe:", prompt)

        x_col = self.df.columns[0]
        y_col = self.df.columns[1]
        self.df[x_col] = self.df[x_col].astype(str)

        fig, ax = plt.subplots()
        chart_type = chart_type.strip().lower()

        if chart_type in ["barchart", "bar"]:
            self.df.plot(kind="bar", x=x_col, y=y_col, ax=ax, color="#200695")

        elif chart_type in ["linechart", "line"]:
            self.df.plot(kind="line", x=x_col, y=y_col, ax=ax, color="#200695", marker='o')

        elif chart_type in ["scatterchart", "scatter"]:
            self.df[x_col] = self.df[x_col].astype(float)  # for scatter, x must be numeric
            self.df.plot(kind="scatter", x=x_col, y=y_col, ax=ax, color="#200695")

        elif chart_type in ["piechart", "pie"]:
            # Generate random hex colors
            def random_color():
                return "#" + ''.join(random.choices("0123456789ABCDEF", k=6))

            colors = [random_color() for _ in range(len(self.df))]

            fig, ax = plt.subplots()
            self.df.set_index(x_col)[y_col].plot.pie(
                ax=ax, autopct='%1.1f%%', startangle=90, colors=colors
            )
            ax.set_ylabel("")  # Hide y-axis label
            ax.set_title(f"{y_col} distribution by {x_col}")

        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        return fig

@app.route("/generate_chart", methods=["POST"])
def generate_chart():
    try:
        data = request.get_json(force=True, silent=True)
        print(data)
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        chart_type = data.get("chart_type", "")
        num_rows = data.get("num_rows", "All")
        query1 = data.get("query")

        table = execute_mysql_query(query1)
        if not isinstance(table["results"], list) or len(table["results"]) == 0:
            return jsonify({"error": "Table data is missing or not in correct format"}), 400

        df = pd.DataFrame(table["results"])
        print(f"\n📊 Received DataFrame:\n{df}")
        print(f"num_rows type: {type(num_rows)}")

        if isinstance(num_rows, str) and num_rows.lower() == "all":
            if len(df) > 50 and chart_type.lower() in ["bar chart", "histogram", "line chart", "pie chart"]:
                return jsonify({"warning": f"{chart_type} cannot display more than 50 rows. Your dataset has {len(df)} rows."}), 200

        prompt = (
            f"Create a {chart_type} using {'all rows' if num_rows.lower() == 'all' else f'the {num_rows} rows'} of the dataset. "
            "Use Hexcode: #200695 for the color. Make it visually clear and labeled."
        )

        smart_df = SmartDataframe(df)
        try:
            result = smart_df.chat(prompt,chart_type)
        except Exception:
            print("🔥 chart  failed!")
            print(traceback.format_exc())
            return jsonify({"error": "chat generation failed"}), 500

        # Save the chart image
        chart_dir = "static/charts"
        os.makedirs(chart_dir, exist_ok=True)
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = os.path.join(chart_dir, filename)

        encoded_image = None
        if isinstance(result, plt.Figure):
            result.savefig(file_path)
            result.clf()

            # Open the image file locally (optional)
            webbrowser.open(f"file://{os.path.abspath(file_path)}")

            # Convert to base64 for API response
            with open(file_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        if not encoded_image:
            return jsonify({"error": "Chart was not generated properly."}), 500

        return jsonify({
            "status": "success",
            "image": encoded_image,
            "image_url": f"/static/charts/{filename}"
        })

    except Exception as e:
        print("🔥 Server Error:")
        print(traceback.format_exc())
        return jsonify({"error": f"Server error: {str(e)}"}), 500










@app.route("/clear_conversation", methods=["POST"])
def clear_conversation():
    conversation_id = request.json.get("conversation_id")
    try:
        with closing(sqlite3.connect("database.db")) as conn, closing(conn.cursor()) as cursor:
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON;")

            # Delete conversation (will also delete messages due to ON DELETE CASCADE)
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            conn.commit()

        return jsonify({"message": "Conversation and linked messages deleted."})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="0.0.0.0", port=8000)