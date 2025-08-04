# Snowflake MCP Server

A secure [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for executing SQL queries against Snowflake. This server enables AI assistants like Claude and Cursor to interact with your Snowflake data warehouse safely and efficiently.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🔐 **Multiple Authentication Methods**: Password, private key, and SSO authentication
- 🛡️ **Secure Configuration**: Environment-based configuration with no hard-coded credentials
- ⚡ **Performance Optimized**: Configurable row limits and efficient query execution
- 🔍 **Comprehensive Error Handling**: Detailed error messages with troubleshooting tips
- 📊 **Rich Output Formatting**: Well-formatted query results with metadata
- 🏗️ **MCP Compliant**: Full compatibility with Claude Desktop and Cursor

## Quick Start

### 1. Install
```bash
git clone https://github.com/yourusername/snowflake-mcp-server.git
cd snowflake-mcp-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
nano .env  # Add your Snowflake credentials
```

### 3. Test
```bash
npx @modelcontextprotocol/inspector python snowflake_mcp_server.py
```

## Configuration

### Environment Variables

**Required:**
```bash
SNOWFLAKE_ACCOUNT=your-account-identifier  # e.g., abc12345.us-east-1.snowflakecomputing.com
SNOWFLAKE_USERNAME=your-username
```

**Authentication (choose one):**
```bash
# Option 1: Password
SNOWFLAKE_PASSWORD=your-password

# Option 2: Private Key (recommended)
SNOWFLAKE_PRIVATE_KEY_PATH=/path/to/rsa_key.p8
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=passphrase  # optional

# Option 3: SSO
SNOWFLAKE_AUTHENTICATOR=externalbrowser
```

**Optional:**
```bash
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_MAX_ROWS=1000
```

### Private Key Setup (Recommended)

1. **Generate key pair:**
```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

2. **Add public key to Snowflake:**
```sql
ALTER USER your_username SET RSA_PUBLIC_KEY='your-public-key-content';
```

## Claude Desktop Integration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

**Method 1: Using uv (Recommended)**
```json
{
  "mcpServers": {
    "snowflake": {
      "command": "/opt/homebrew/bin/uv",
      "args": ["--directory", "/path/to/your/project", "run", "snowflake_mcp_server.py"]
    }
  }
}
```

**Method 2: Direct Python**
```json
{
  "mcpServers": {
    "snowflake": {
      "command": "/path/to/your/project/venv/bin/python",
      "args": ["/path/to/your/project/snowflake_mcp_server.py"]
    }
  }
}
```

Set environment variables in your shell profile (`~/.zshrc` or `~/.bash_profile`):
```bash
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USERNAME="your-username"
export SNOWFLAKE_PASSWORD="your-password"  # or private key variables
```

Restart Claude Desktop and verify connection with the 🔌 icon.

## Cursor Integration

The server integrates with [Cursor](https://docs.cursor.com/en/context/mcp) for AI-powered database operations in your IDE.

**Project Configuration (Recommended)**

Create `.cursor/mcp.json` in your project root:
```json
{
  "mcpServers": {
    "snowflake": {
      "command": "/path/to/your/project/venv/bin/python",
      "args": ["/path/to/your/project/snowflake_mcp_server.py"],
      "env": {
        "SNOWFLAKE_ACCOUNT": "your-account",
        "SNOWFLAKE_USERNAME": "your-username",
        "SNOWFLAKE_PASSWORD": "your-password"
      }
    }
  }
}
```

**Global Configuration**

Create `~/.cursor/mcp.json` for system-wide access and set environment variables in your shell profile.

### Usage in Cursor

The Composer Agent automatically detects MCP tools. Example prompts:
```
"What's the schema of our users table?"
"Show me sales data for the last quarter"
"Find customers with orders over $10,000"
```

**Features:**
- Tool approval/auto-run modes
- Expandable tool responses
- Error handling with suggestions
- Multi-step operations

## Example Prompts

```
"Show me the top 10 customers by revenue"
"What tables are available in my database?"
"Describe the schema of the ORDERS table"
"Count records created this month"
"Help me optimize this slow query"
```

## Security Best Practices

⚠️ **IMPORTANT SECURITY NOTICE**: This server executes raw SQL queries on your Snowflake instance. Always follow these security practices:

1. **Use private key authentication** instead of passwords
2. **Create dedicated Snowflake user** with minimal permissions:
```sql
CREATE USER mcp_user PASSWORD = 'secure_password';
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO USER mcp_user;
GRANT USAGE ON DATABASE your_db TO USER mcp_user;
GRANT SELECT ON ALL TABLES IN SCHEMA your_db.public TO USER mcp_user;
```
3. **Secure private keys:** `chmod 600 /path/to/rsa_key.p8`
4. **Use environment variables** - never hard-code credentials
5. **Use project-specific configurations** for sensitive environments
6. **⚠️ SQL Injection Risk**: This server executes any SQL query provided by AI assistants. Ensure:
   - Your Snowflake user has **minimal required permissions**
   - **No admin or elevated privileges** for the MCP user
   - Consider using **read-only access** for sensitive environments
   - **Monitor query logs** for unexpected operations
7. **Network Security**: Ensure proper firewall rules and VPN access if required

## Troubleshooting

### Common Issues

**Environment Variables Not Set:**
- Check `.env` file format (no quotes, no spaces around `=`)
- Set variables in shell profile for global access

**Connection Errors:**
- Verify account identifier format (include region if needed)
- Check network connectivity and warehouse status
- Verify credentials and permissions

**Authentication Failures:**
- For private key: Ensure public key is set in Snowflake
- For SSO: Test browser login first
- Check if user account is locked

**Path Issues:**
- Use absolute paths in configuration files
- Verify paths with `which uv` or `which python`

### Debug Mode

**Server Logs:**
```bash
export MCP_LOG_LEVEL=DEBUG
python snowflake_mcp_server.py
```

**Client Logs:**
- Claude Desktop: `~/Library/Logs/Claude/mcp*.log`
- Cursor: Output panel → "MCP Logs"

## Development

```bash
git clone https://github.com/yourusername/snowflake-mcp-server.git
cd snowflake-mcp-server
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Note**: This project is not officially affiliated with Snowflake Inc. or Anthropic. 