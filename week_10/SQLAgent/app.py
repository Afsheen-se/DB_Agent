"""
SQL Agent Web Interface
A simple Flask web application for interacting with SQL Agent using natural language
"""

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import sqlalchemy
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.schema import SystemMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database Configuration
DB_URL = "sqlite:///sql_agent_class.db"
engine = sqlalchemy.create_engine(DB_URL)

class QueryInput(BaseModel):
    sql: str = Field(description="A single read-only SELECT statement")

class SafeSQLTool(BaseTool):
    name: str = "execute_sql"
    description: str = "Execute a safe SQL SELECT query on the database"
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, sql: str) -> str:
        # Security validation
        s = sql.strip()
        
        # Check for dangerous operations
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE)\b", s, re.I):
            return "ERROR: Write operations are not allowed for security reasons."
        
        # Check for multiple statements
        if ";" in s and not s.strip().endswith(";"):
            return "ERROR: Multiple statements are not allowed."
        
        # Ensure it's a SELECT statement
        if not re.match(r"(?is)^\s*select\b", s):
            return "ERROR: Only SELECT statements are allowed."
        
        # Add LIMIT if not present
        if not re.search(r"\blimit\s+\d+\b", s, re.I):
            s += " LIMIT 50"
        
        try:
            with engine.connect() as conn:
                result = conn.exec_driver_sql(s)
                rows = result.fetchall()
                columns = result.keys()
                
                if not rows:
                    return "Query executed successfully but returned no results."
                
                # Format results as JSON for frontend
                result_data = {
                    "columns": list(columns),
                    "rows": [list(row) for row in rows],
                    "row_count": len(rows)
                }
                
                return f"SUCCESS: {result_data}"
                
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError

# Initialize the SQL Agent
def get_sql_agent():
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        
        system_message = """You are a helpful SQL assistant for an e-commerce database. 
        You can execute SELECT queries to help users analyze data.
        
        Available tables:
        - customers: id, name, email, created_at, region
        - products: id, name, category, price_cents
        - orders: id, customer_id, order_date, status
        - order_items: id, order_id, product_id, quantity, unit_price_cents
        - payments: id, order_id, amount_cents, paid_at, method, status
        - refunds: id, order_id, amount_cents, refunded_at, reason
        
        Always use proper JOINs when needed and explain your results clearly.
        Be helpful and provide insights about the data."""
        
        tool = SafeSQLTool()
        agent = initialize_agent(
            tools=[tool],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            agent_kwargs={"system_message": SystemMessage(content=system_message)}
        )
        
        return agent
    except Exception as e:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query_agent():
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Check for quota exceeded error and provide fallback
        try:
            agent = get_sql_agent()
            if not agent:
                return jsonify({'error': 'Failed to initialize SQL agent. Check your API key.'}), 500
            
            # Execute the query
            response = agent.invoke({"input": user_query})
            result = response['output']
            
            # Check if result contains structured data
            if result.startswith("SUCCESS: "):
                import json
                try:
                    data_part = result[9:]  # Remove "SUCCESS: " prefix
                    structured_data = json.loads(data_part)
                    return jsonify({
                        'success': True,
                        'data': structured_data,
                        'message': f"Query executed successfully. Found {structured_data['row_count']} rows."
                    })
                except:
                    return jsonify({
                        'success': True,
                        'message': result,
                        'data': None
                    })
            else:
                return jsonify({
                    'success': False,
                    'message': result,
                    'data': None
                })
                
        except Exception as api_error:
            error_msg = str(api_error)
            if "429" in error_msg or "quota" in error_msg.lower():
                # API quota exceeded - provide fallback response
                return handle_quota_exceeded(user_query)
            else:
                return jsonify({'error': f'Server error: {error_msg}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def handle_quota_exceeded(user_query):
    """Handle API quota exceeded by providing direct database responses"""
    try:
        # Simple keyword-based fallback responses
        query_lower = user_query.lower()
        
        if "customers" in query_lower:
            return get_customers_data()
        elif "products" in query_lower:
            return get_products_data()
        elif "orders" in query_lower:
            return get_orders_data()
        elif "revenue" in query_lower or "total" in query_lower:
            return get_revenue_data()
        else:
            return jsonify({
                'success': False,
                'message': 'API quota exceeded. Please try again later or upgrade your plan. For now, try asking about "customers", "products", or "orders".',
                'data': None
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'API quota exceeded and fallback failed: {str(e)}',
            'data': None
        })

def get_customers_data():
    """Get customers data directly from database"""
    try:
        with engine.connect() as conn:
            result = conn.exec_driver_sql("SELECT * FROM customers LIMIT 20")
            rows = result.fetchall()
            columns = result.keys()
            
            return jsonify({
                'success': True,
                'data': {
                    'columns': list(columns),
                    'rows': [list(row) for row in rows],
                    'row_count': len(rows)
                },
                'message': f"Found {len(rows)} customers (API quota exceeded, showing direct database results)"
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Database error: {str(e)}',
            'data': None
        })

def get_products_data():
    """Get products data directly from database"""
    try:
        with engine.connect() as conn:
            result = conn.exec_driver_sql("SELECT * FROM products LIMIT 20")
            rows = result.fetchall()
            columns = result.keys()
            
            return jsonify({
                'success': True,
                'data': {
                    'columns': list(columns),
                    'rows': [list(row) for row in rows],
                    'row_count': len(rows)
                },
                'message': f"Found {len(rows)} products (API quota exceeded, showing direct database results)"
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Database error: {str(e)}',
            'data': None
        })

def get_orders_data():
    """Get orders data directly from database"""
    try:
        with engine.connect() as conn:
            result = conn.exec_driver_sql("SELECT * FROM orders LIMIT 20")
            rows = result.fetchall()
            columns = result.keys()
            
            return jsonify({
                'success': True,
                'data': {
                    'columns': list(columns),
                    'rows': [list(row) for row in rows],
                    'row_count': len(rows)
                },
                'message': f"Found {len(rows)} orders (API quota exceeded, showing direct database results)"
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Database error: {str(e)}',
            'data': None
        })

def get_revenue_data():
    """Get revenue data directly from database"""
    try:
        with engine.connect() as conn:
            result = conn.exec_driver_sql("""
                SELECT 
                    SUM(oi.quantity * oi.unit_price_cents) as total_revenue_cents,
                    COUNT(DISTINCT o.id) as total_orders,
                    COUNT(DISTINCT o.customer_id) as total_customers
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
            """)
            rows = result.fetchall()
            columns = result.keys()
            
            return jsonify({
                'success': True,
                'data': {
                    'columns': list(columns),
                    'rows': [list(row) for row in rows],
                    'row_count': len(rows)
                },
                'message': f"Revenue analysis (API quota exceeded, showing direct database results)"
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Database error: {str(e)}',
            'data': None
        })

@app.route('/api/schema')
def get_schema():
    try:
        with engine.connect() as conn:
            # Get all tables
            result = conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in result.fetchall()]
            
            schema_info = {}
            for table in tables:
                result = conn.exec_driver_sql(f"PRAGMA table_info({table})")
                columns = result.fetchall()
                schema_info[table] = [
                    {'name': col[1], 'type': col[2], 'nullable': not col[3]}
                    for col in columns
                ]
            
            return jsonify({'schema': schema_info})
    except Exception as e:
        return jsonify({'error': f'Failed to get schema: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
