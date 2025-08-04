"""
Snowflake MCP Server

A secure MCP server for executing SQL queries against Snowflake with configurable authentication.
Supports multiple authentication methods including key-pair, password, and SSO.
"""

import os
import sys
import json
from typing import Optional, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import pandas as pd
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# Load environment variables from .env file
load_dotenv()


class SnowflakeConfig:
    """Configuration management for Snowflake connection."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Required settings
        self.account_identifier = self._get_required_env("SNOWFLAKE_ACCOUNT")
        self.username = self._get_required_env("SNOWFLAKE_USERNAME")
        
        # Authentication settings (at least one method must be configured)
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.private_key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
        self.private_key_passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
        self.authenticator = os.getenv("SNOWFLAKE_AUTHENTICATOR", "snowflake")
        
        # Optional connection settings with defaults
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = os.getenv("SNOWFLAKE_DATABASE")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA")
        self.role = os.getenv("SNOWFLAKE_ROLE")
        
        # Query settings
        self.max_rows = int(os.getenv("SNOWFLAKE_MAX_ROWS", "1000"))
        
        # Validate configuration
        self._validate_config()
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _validate_config(self):
        """Validate that at least one authentication method is configured."""
        has_password = bool(self.password)
        has_private_key = bool(self.private_key_path)
        has_sso = self.authenticator != "snowflake"
        
        if not (has_password or has_private_key or has_sso):
            raise ValueError(
                "At least one authentication method must be configured:\n"
                "- Set SNOWFLAKE_PASSWORD for password authentication\n"
                "- Set SNOWFLAKE_PRIVATE_KEY_PATH for key-pair authentication\n"
                "- Set SNOWFLAKE_AUTHENTICATOR for SSO authentication"
            )
        
        if has_private_key:
            key_path = Path(self.private_key_path)
            if not key_path.exists():
                raise ValueError(f"Private key file not found: {self.private_key_path}")
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters for Snowflake connector."""
        params = {
            "account": self.account_identifier,
            "user": self.username,
            "authenticator": self.authenticator,
        }
        
        # Add optional connection settings
        if self.warehouse:
            params["warehouse"] = self.warehouse
        if self.database:
            params["database"] = self.database
        if self.schema:
            params["schema"] = self.schema
        if self.role:
            params["role"] = self.role
        
        # Add authentication method
        if self.password:
            params["password"] = self.password
        elif self.private_key_path:
            params["private_key"] = self._load_private_key()
        
        return params
    
    def _load_private_key(self):
        """Load and return the private key for authentication."""
        try:
            with open(self.private_key_path, 'rb') as key_file:
                key_data = key_file.read()
            
            passphrase = self.private_key_passphrase.encode() if self.private_key_passphrase else None
            private_key = load_pem_private_key(
                key_data,
                password=passphrase,
                backend=default_backend()
            )
            return private_key
        except Exception as e:
            raise ValueError(f"Failed to load private key from {self.private_key_path}: {str(e)}")


def log_error(message: str):
    """Log error to stderr to avoid interfering with MCP protocol."""
    print(f"[SNOWFLAKE-MCP] {message}", file=sys.stderr)


def log_info(message: str):
    """Log info to stderr to avoid interfering with MCP protocol."""
    print(f"[SNOWFLAKE-MCP] {message}", file=sys.stderr)


# Initialize configuration
try:
    config = SnowflakeConfig()
    log_info("Snowflake MCP server configuration loaded successfully")
except Exception as e:
    log_error(f"Configuration error: {str(e)}")
    sys.exit(1)

# Initialize FastMCP server
mcp = FastMCP(
    "Snowflake MCP Server", 
    dependencies=["snowflake-connector-python", "pandas", "cryptography"]
)


def execute_snowflake_query(
    sql_query: str, 
    database: Optional[str] = None, 
    schema: Optional[str] = None, 
    warehouse: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a SQL query on Snowflake with proper error handling.
    
    Args:
        sql_query: The SQL query to execute
        database: Override the default database
        schema: Override the default schema  
        warehouse: Override the default warehouse
    
    Returns:
        Dictionary containing query results and metadata
    """
    conn = None
    cursor = None
    
    log_info(f"Executing query: {sql_query[:50]}{'...' if len(sql_query) > 50 else ''}")
    
    try:
        # Get connection parameters
        conn_params = config.get_connection_params()
        
        # Override with function parameters if provided
        if database:
            conn_params["database"] = database
        if schema:
            conn_params["schema"] = schema
        if warehouse:
            conn_params["warehouse"] = warehouse
        
        # Connect to Snowflake
        log_info("Connecting to Snowflake...")
        conn = snowflake.connector.connect(**conn_params)
        
        # Execute the query
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Handle different types of queries
        if cursor.description:
            # Query returned data
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchmany(config.max_rows)
            row_count = len(data)
            
            # Check if results were truncated
            remaining_rows = cursor.fetchone()
            truncated = remaining_rows is not None
            if truncated:
                # Put the row back for accurate count if possible
                total_rows = f"{row_count}+"
            else:
                total_rows = str(row_count)
            
            df = pd.DataFrame(data, columns=columns)
            
            # Get current context
            context = {
                "database": conn_params.get("database", "N/A"),
                "schema": conn_params.get("schema", "N/A"), 
                "warehouse": conn_params.get("warehouse", "N/A")
            }
            
            try:
                cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()")
                context_row = cursor.fetchone()
                if context_row:
                    context = {
                        "database": context_row[0] or "N/A",
                        "schema": context_row[1] or "N/A",
                        "warehouse": context_row[2] or "N/A"
                    }
            except Exception as e:
                log_error(f"Could not retrieve current context: {str(e)}")
            
            return {
                "success": True,
                "result_df": df,
                "sql_query": sql_query,
                "row_count": row_count,
                "total_rows": total_rows,
                "column_count": len(columns),
                "context": context,
                "truncated": truncated
            }
        else:
            # DDL/DML query with no result set
            log_info("Query executed successfully (no result set)")
            affected_rows = cursor.rowcount if cursor.rowcount >= 0 else 0
            
            return {
                "success": True,
                "result_df": pd.DataFrame({"status": [f"Statement executed successfully. Rows affected: {affected_rows}"]}),
                "sql_query": sql_query,
                "row_count": 1,
                "total_rows": "1", 
                "column_count": 1,
                "context": {
                    "database": conn_params.get("database", "N/A"),
                    "schema": conn_params.get("schema", "N/A"),
                    "warehouse": conn_params.get("warehouse", "N/A")
                },
                "truncated": False,
                "affected_rows": affected_rows
            }
    
    except snowflake.connector.errors.ProgrammingError as e:
        error_msg = f"SQL Error: {str(e)}"
        log_error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "sql_query": sql_query,
            "error_type": "SQL_ERROR"
        }
    
    except snowflake.connector.errors.DatabaseError as e:
        error_msg = f"Database Error: {str(e)}"
        log_error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "sql_query": sql_query,
            "error_type": "DATABASE_ERROR"
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "sql_query": sql_query,
            "error_type": "SYSTEM_ERROR"
        }
    
    finally:
        # Clean up resources
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            log_info("Database connection closed")
        except Exception as e:
            log_error(f"Error closing connection: {str(e)}")


@mcp.tool()
async def execute_snowflake_sql_query(
    query: str, 
    database: Optional[str] = None, 
    schema: Optional[str] = None, 
    warehouse: Optional[str] = None
) -> str:
    """
    Execute any SQL query on Snowflake.
    
    ⚠️  SECURITY WARNING: This tool executes raw SQL queries on your Snowflake instance.
    Ensure proper user permissions and network security. Consider query restrictions
    for production environments.
    
    Args:
        query: The SQL query to execute (required)
        database: Override the default database (optional)
        schema: Override the default schema (optional)
        warehouse: Override the default warehouse (optional)
    
    Returns:
        Formatted string containing query results or error message
    """
    if not query or not query.strip():
        return "Error: Query cannot be empty"
    
    # Security check: Warn about potentially dangerous operations
    query_upper = query.strip().upper()
    dangerous_operations = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE USER', 'GRANT', 'REVOKE']
    
    for operation in dangerous_operations:
        if query_upper.startswith(operation):
            log_info(f"🚨 SECURITY ALERT: Executing potentially dangerous operation: {operation}")
            break
    
    # Log query (sanitized - only first 50 chars to avoid logging sensitive data)
    log_info(f"Executing query: {query[:50]}{'...' if len(query) > 50 else ''}")
    
    # Execute the query
    result = execute_snowflake_query(query.strip(), database, schema, warehouse)
    
    if result["success"]:
        # Format successful result
        output_lines = [
            "✅ Query executed successfully",
            "",
            f"SQL: {result['sql_query']}",
            "",
            f"Context: Database={result['context']['database']}, "
            f"Schema={result['context']['schema']}, "
            f"Warehouse={result['context']['warehouse']}",
            ""
        ]
        
        # Add result summary
        if result.get("affected_rows") is not None:
            output_lines.append(f"Rows affected: {result['affected_rows']}")
        else:
            if result["truncated"]:
                output_lines.append(
                    f"Results: {result['total_rows']} rows (showing first {result['row_count']}), "
                    f"{result['column_count']} columns"
                )
            else:
                output_lines.append(
                    f"Results: {result['row_count']} rows, {result['column_count']} columns"
                )
        
        output_lines.extend(["", "Data:"])
        
        # Format the dataframe
        try:
            with pd.option_context(
                'display.max_colwidth', 50,
                'display.width', 200,
                'display.max_rows', None
            ):
                df_str = result["result_df"].to_string(index=False)
                output_lines.append(df_str)
        except Exception as e:
            log_error(f"Error formatting results: {str(e)}")
            output_lines.extend([
                "Error formatting results for display.",
                f"Data shape: {result['result_df'].shape}",
                "Raw data available but too complex to display."
            ])
        
        if result["truncated"]:
            output_lines.extend([
                "",
                f"⚠️  Results truncated. Showing first {config.max_rows} rows only.",
                "Consider adding LIMIT clause or filtering your query for better performance."
            ])
        
        return "\n".join(output_lines)
    
    else:
        # Format error result
        error_type = result.get("error_type", "UNKNOWN_ERROR")
        error_lines = [
            f"❌ Query failed ({error_type})",
            "",
            f"SQL: {result['sql_query']}",
            "",
            f"Error: {result['error']}",
        ]
        
        # Add helpful tips based on error type
        if error_type == "SQL_ERROR":
            error_lines.extend([
                "",
                "💡 Tips:",
                "- Check your SQL syntax",
                "- Verify table and column names",
                "- Ensure you have proper permissions"
            ])
        elif error_type == "DATABASE_ERROR":
            error_lines.extend([
                "",
                "💡 Tips:",
                "- Check your connection settings",
                "- Verify database/schema exists",
                "- Ensure warehouse is running"
            ])
        
        error_msg = "\n".join(error_lines)
        log_error(f"Query failed: {result['error']}")
        return error_msg


if __name__ == "__main__":
    try:
        log_info("Starting Snowflake MCP server...")
        log_info(f"Configuration: Account={config.account_identifier}, User={config.username}")
        log_info(f"Max rows limit: {config.max_rows}")
        
        # Run the MCP server
        mcp.run()
        
    except KeyboardInterrupt:
        log_info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        log_error(f"Failed to start server: {str(e)}")
        sys.exit(1)