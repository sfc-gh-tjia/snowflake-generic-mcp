# General-Purpose Snowflake MCP Server

A secure [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that provides AI assistants with safe, efficient access to your Snowflake data warehouse. Execute SQL queries, analyze data, and get insights through natural language interactions. 

For more detail information and example usages, reference the [Blog](https://medium.com/@uniquejtx_3744/the-general-purpose-snowflake-mcp-server-sql-operation-through-natural-language-ddd33bba4fa7).

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Key Features

- 🔐 **Multiple Authentication**: Password, private key, and SSO support
- 🛡️ **Security First**: Environment-based config, no hard-coded credentials
- ⚡ **Performance Optimized**: Configurable limits and efficient query execution  
- 🔍 **Smart Error Handling**: Detailed messages with troubleshooting guidance
- 📊 **Rich Query Results**: Formatted tables with metadata and row counts
- 🧠 **AI-Ready**: Natural language to SQL through MCP protocol
- 🏗️ **Universal Compatibility**: Works with any MCP-compatible AI client

## Quick Start

### 1. Install
```bash
git clone https://github.com/uniquejtx/snowflake-generic-mcp.git
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
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_MAX_ROWS=100
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

Connect the MCP server to your AI assistant for natural language database interactions.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Cursor

**Option 1**: Project-specific in Cursor Settings → Tools & Integration → MCP tools  
**Option 2**: Global config in `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "snowflake": {
      "command": "/opt/homebrew/bin/uv", 
      "args": ["--directory", "/absolute/path/to/your/project", "run", "snowflake_mcp_server.py"]
    }
  }
}
```

## Example Usage

Once connected, you can interact with your Snowflake data using natural language:

```
"What tables are available in my database?"
"Show me the schema of the users table"
"Find all customers who made purchases this month"
"Analyze sales trends for Q4"
"Help me optimize this slow query"
"Count records in each table"
"Show me the top 10 customers by revenue"
```

The server handles:
- **Query execution** with proper formatting and metadata
- **Error handling** with helpful troubleshooting suggestions  
- **Security logging** for dangerous operations
- **Performance limits** to prevent resource exhaustion

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

## License

MIT License - see [LICENSE](LICENSE) file for details.