# MCP Email Server Skill

> **Tier:** Silver  
> **Status:** Ready to Implement  
> **Dependencies:** Node.js, Gmail API or SMTP

---

## 📋 Overview

The MCP (Model Context Protocol) Email Server enables Qwen/Claude to send emails through an MCP server. This fulfills the Silver tier requirement for "One working MCP server for external action."

**Use Case:** Send email responses, notifications, and reports automatically after human approval.

---

## 🎯 Silver Tier Requirement

This skill fulfills:
- ✅ "One working MCP server for external action (e.g., sending emails)"
- ✅ "Human-in-the-loop approval workflow for sensitive actions"
- ✅ Part of the Action layer (MCP servers)

---

## 📦 Prerequisites

### 1. Node.js

```bash
# Check Node.js version (need v24+ LTS)
node --version

# Install from https://nodejs.org/ if needed
```

### 2. Gmail API Credentials (if using Gmail)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download `credentials.json`

### 3. OR SMTP Credentials (if using SMTP)

- SMTP server address
- Port (587 for TLS, 465 for SSL)
- Username and password

---

## 🏗️ Implementation

### Option A: Gmail MCP Server

**File:** `scripts/mcp-email-server/index.js`

```javascript
#!/usr/bin/env node

/**
 * MCP Email Server for AI Employee
 * 
 * Sends emails via Gmail API or SMTP
 * 
 * Usage:
 *   node index.js
 * 
 * MCP Tools:
 *   - email_send: Send an email
 *   - email_draft: Create a draft email
 *   - email_search: Search sent emails
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

// Configuration
const GMAIL_CREDENTIALS_PATH = process.env.GMAIL_CREDENTIALS || './credentials.json';
const GMAIL_TOKEN_PATH = process.env.GMAIL_TOKEN_PATH || './gmail_token.json';

// Create MCP server
const server = new Server(
  {
    name: 'email-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'email_send',
        description: 'Send an email via Gmail API',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject',
            },
            body: {
              type: 'string',
              description: 'Email body (plain text or HTML)',
            },
            isHtml: {
              type: 'boolean',
              description: 'Whether body is HTML (default: false)',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'email_draft',
        description: 'Create a draft email (requires approval before sending)',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject',
            },
            body: {
              type: 'string',
              description: 'Email body',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'email_search',
        description: 'Search sent emails',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Gmail search query',
            },
            maxResults: {
              type: 'number',
              description: 'Maximum results to return (default: 10)',
            },
          },
          required: ['query'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'email_send') {
      return await sendEmail(args);
    } else if (name === 'email_draft') {
      return await createDraft(args);
    } else if (name === 'email_search') {
      return await searchEmails(args);
    } else {
      throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

/**
 * Send an email via Gmail API
 */
async function sendEmail({ to, subject, body, isHtml = false }) {
  const auth = await getAuthClient();
  const gmail = google.gmail({ version: 'v1', auth });

  // Create email message
  const message = createMessage(to, subject, body, isHtml);

  // Send email
  const response = await gmail.users.messages.send({
    userId: 'me',
    requestBody: message,
  });

  return {
    content: [
      {
        type: 'text',
        text: `Email sent successfully! Message ID: ${response.data.id}`,
      },
    ],
  };
}

/**
 * Create a draft email
 */
async function createDraft({ to, subject, body }) {
  const auth = await getAuthClient();
  const gmail = google.gmail({ version: 'v1', auth });

  const message = createMessage(to, subject, body);

  const response = await gmail.users.drafts.create({
    userId: 'me',
    requestBody: {
      message: message,
    },
  });

  return {
    content: [
      {
        type: 'text',
        text: `Draft created! Draft ID: ${response.data.id}. Review in Gmail and send when ready.`,
      },
    ],
  };
}

/**
 * Search sent emails
 */
async function searchEmails({ query, maxResults = 10 }) {
  const auth = await getAuthClient();
  const gmail = google.gmail({ version: 'v1', auth });

  const response = await gmail.users.messages.list({
    userId: 'me',
    q: `in:sent ${query}`,
    maxResults: maxResults,
  });

  const messages = response.data.messages || [];

  return {
    content: [
      {
        type: 'text',
        text: `Found ${messages.length} emails. IDs: ${messages.map(m => m.id).join(', ')}`,
      },
    ],
  };
}

/**
 * Create RFC 2822 email message
 */
function createMessage(to, subject, body, isHtml = false) {
  const contentType = isHtml ? 'text/html; charset="utf-8"' : 'text/plain; charset="utf-8"';
  
  const parts = [
    'From: AI Employee <me>',
    `To: ${to}`,
    `Subject: ${subject}`,
    'MIME-Version: 1.0',
    `Content-Type: ${contentType}`,
    '',
    body,
  ];

  const message = parts.join('\n');
  const encodedMessage = Buffer.from(message).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

  return {
    raw: encodedMessage,
  };
}

/**
 * Get authenticated Gmail client
 */
async function getAuthClient() {
  const credentials = JSON.parse(fs.readFileSync(GMAIL_CREDENTIALS_PATH, 'utf-8'));
  
  let tokens = null;
  if (fs.existsSync(GMAIL_TOKEN_PATH)) {
    tokens = JSON.parse(fs.readFileSync(GMAIL_TOKEN_PATH, 'utf-8'));
  }

  const oauth2Client = new google.auth.OAuth2(
    credentials.client_id,
    credentials.client_secret,
    credentials.redirect_uris[0]
  );

  if (tokens) {
    oauth2Client.setCredentials(tokens);
  } else {
    throw new Error('No Gmail token found. Please authenticate first.');
  }

  return oauth2Client;
}

/**
 * Initialize authentication (run separately to get token)
 */
async function authenticate() {
  const credentials = JSON.parse(fs.readFileSync(GMAIL_CREDENTIALS_PATH, 'utf-8'));
  
  const { authenticate: gAuth } = await import('google-auth-library');
  const auth = new gAuth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.compose'],
  });

  // This would open browser for OAuth flow
  // For simplicity, use the gmail_watcher token if available
  console.log('Authentication would open browser here...');
  console.log('For now, reuse token from gmail_watcher setup');
}

// Start server
async function main() {
  if (process.argv.includes('--authenticate')) {
    await authenticate();
    return;
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP Email Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
```

---

### Option B: Simple SMTP MCP Server

**File:** `scripts/mcp-email-server-smtp/index.js`

```javascript
#!/usr/bin/env node

/**
 * Simple SMTP MCP Email Server
 * 
 * Uses nodemailer for SMTP-based email sending
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const nodemailer = require('nodemailer');

// Configuration from environment
const SMTP_HOST = process.env.SMTP_HOST || 'smtp.gmail.com';
const SMTP_PORT = parseInt(process.env.SMTP_PORT) || 587;
const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASS = process.env.SMTP_PASS;

// Create transporter
const transporter = nodemailer.createTransport({
  host: SMTP_HOST,
  port: SMTP_PORT,
  secure: SMTP_PORT === 465,
  auth: {
    user: SMTP_USER,
    pass: SMTP_PASS,
  },
});

// Create MCP server
const server = new Server(
  {
    name: 'email-mcp-smtp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'email_send',
        description: 'Send an email via SMTP',
        inputSchema: {
          type: 'object',
          properties: {
            to: { type: 'string', description: 'Recipient email' },
            subject: { type: 'string', description: 'Email subject' },
            body: { type: 'string', description: 'Email body' },
            isHtml: { type: 'boolean', description: 'HTML body' },
          },
          required: ['to', 'subject', 'body'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'email_send') {
    try {
      const info = await transporter.sendMail({
        from: SMTP_USER,
        to: args.to,
        subject: args.subject,
        text: args.body,
        html: args.isHtml ? args.body : null,
      });

      return {
        content: [{ type: 'text', text: `Email sent! Message ID: ${info.messageId}` }],
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true,
      };
    }
  }
});

// Start server
const transport = new StdioServerTransport();
server.connect(transport);
console.error('SMTP Email MCP Server running');
```

---

## 📦 Package Configuration

**File:** `scripts/mcp-email-server/package.json`

```json
{
  "name": "email-mcp-server",
  "version": "1.0.0",
  "description": "MCP Email Server for AI Employee",
  "main": "index.js",
  "bin": {
    "email-mcp": "./index.js"
  },
  "scripts": {
    "start": "node index.js",
    "authenticate": "node index.js --authenticate"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "googleapis": "^131.0.0",
    "google-auth-library": "^9.0.0"
  }
}
```

**For SMTP version:**
```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "nodemailer": "^6.9.0"
  }
}
```

---

## 🔧 Configuration

### MCP Configuration for Qwen/Claude

**File:** `~/.config/qwen-code/mcp.json` (or equivalent)

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/mcp-email-server/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json",
        "GMAIL_TOKEN_PATH": "/path/to/gmail_token.json"
      }
    }
  ]
}
```

### Environment Variables

Create `.env` file:

```bash
# Gmail MCP
GMAIL_CREDENTIALS=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/gmail_token.json

# OR SMTP MCP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

---

## 🚀 Usage

### Installation

```bash
# Navigate to MCP server folder
cd AI_Employee_Vault/scripts/mcp-email-server

# Install dependencies
npm install

# Authenticate (Gmail only)
npm run authenticate

# Start server (stdio mode for MCP)
node index.js
```

### With Qwen

```bash
# Send an email
qwen "Use the email MCP server to send an email to test@example.com with subject 'Test' and body 'Hello from AI Employee'"

# Create a draft (requires approval)
qwen "Create a draft email to client@example.com about the project update"
```

### Human-in-the-Loop Workflow

```bash
# 1. Qwen creates approval request
qwen "Create an approval request for sending invoice email"

# 2. User reviews and approves (moves file to Approved/)

# 3. Qwen sends email via MCP
qwen "Check Approved folder and send approved emails"
```

---

## 📁 Approval Workflow Example

### 1. Qwen Creates Approval Request

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #123 - March 2026
created: 2026-03-14T10:30:00
status: pending
---

## Email to Send

**To:** client@example.com  
**Subject:** Invoice #123 - March 2026

**Body:**
```
Dear Client,

Please find attached invoice #123 for March 2026.

Amount: $1,500.00
Due: March 30, 2026

Thank you for your business!

Best regards,
AI Employee
```

## To Approve
Move this file to /Approved folder.

## To Reject
Move to /Rejected or delete this file.
```

### 2. User Approves

User moves file from `Pending_Approval/` to `Approved/`

### 3. Qwen Executes via MCP

```bash
qwen "Send the approved email in Approved/INVOICE_email.md"
```

---

## 🐛 Troubleshooting

### Error: "Module not found @modelcontextprotocol/sdk"

**Fix:**
```bash
npm install
```

### Error: "No Gmail token found"

**Fix:** Run authentication or reuse token from Gmail watcher

### Error: "SMTP authentication failed"

**Fix:**
1. Use app-specific password (not regular password)
2. Enable "Less secure app access" (Gmail)
3. Check SMTP credentials

---

## 🔗 Related Skills

| Skill | Purpose |
|-------|---------|
| `gmail_watcher_skill.md` | Receive emails |
| `approval_workflow_skill.md` | Human-in-the-loop approval |
| `plan_generator_skill.md` | Create email plans |

---

## 📚 Resources

- [MCP SDK Documentation](https://modelcontextprotocol.io/)
- [Nodemailer](https://nodemailer.com/)
- [Gmail API](https://developers.google.com/gmail/api)
- [Hackathon Doc Section 2C](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md#action-the-hands)

---

*Skill Version: 1.0*  
*Last Updated: 2026-03-14*  
*Silver Tier Component*
