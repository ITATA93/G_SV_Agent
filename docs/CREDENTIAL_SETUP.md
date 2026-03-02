---
depends_on:
  - docs/TASKS.md
  - docs/ACTIVATION_CHECKLIST.md
impacts:
  - docs/TASKS.md
---

# Credential Setup Guide -- G_SV_Agent

> Step-by-step instructions for obtaining all external API keys and tokens
> required by the GEN_OS ecosystem. Each section covers one credential,
> where to create it, and which `.env` files to update.

---

## 1. Langfuse API Keys (HIGH BLOCKER)

**What:** Public key (`pk-lf-*`) and Secret key (`sk-lf-*`) for LLM observability.
**Where used:** `GEN_OS-master/.env`, `G_DeepResearch_Salud_Chile/.env`

### Steps

1. Go to [https://app.langfuse.com](https://app.langfuse.com) (or your self-hosted instance at `https://langfuse.imedicina.cl`).
2. Log in or create an account.
3. Navigate to **Settings** > **API Keys**.
4. Click **Create API Key**.
5. Copy the **Public Key** (starts with `pk-lf-`) and **Secret Key** (starts with `sk-lf-`).
6. Update the following `.env` files:

```bash
# GEN_OS-master/.env
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_HOST=https://langfuse.imedicina.cl

# G_DeepResearch_Salud_Chile/.env
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
```

### Verification

```bash
curl -s -u "pk-lf-xxx:sk-lf-xxx" https://langfuse.imedicina.cl/api/public/health
# Expected: {"status":"OK"}
```

---

## 2. Notion Integration Token (MEDIUM)

**What:** Internal integration token for Notion API access.
**Where used:** `G_Desktop/.env`, `G_TaskCenter/.env`

### Steps

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations).
2. Click **+ New integration**.
3. Configure:
   - **Name:** `GEN_OS Agent`
   - **Associated workspace:** Select your workspace
   - **Capabilities:** Read content, Update content, Insert content
4. Click **Submit**.
5. Copy the **Internal Integration Secret** (starts with `ntn_` or `secret_`).
6. In Notion, share the relevant databases/pages with the integration:
   - Open the database page > **...** menu > **Add connections** > Select `GEN_OS Agent`.
7. Update `.env` files:

```bash
# G_Desktop/.env
NOTION_TOKEN=ntn_xxxxxxxxxxxxxxxxxxxxxxxx

# G_TaskCenter/.env
NOTION_TOKEN=ntn_xxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=<your-database-id>
```

### Finding Database IDs

Open the database in Notion as a full page. The URL will look like:
```
https://www.notion.so/<workspace>/<database-id>?v=<view-id>
```
The `<database-id>` is the 32-character hex string before the `?`.

### Verification

```bash
curl -s https://api.notion.com/v1/users/me \
  -H "Authorization: Bearer ntn_xxx" \
  -H "Notion-Version: 2022-06-28"
# Expected: JSON with bot user info
```

---

## 3. Azure AD App Registration (MEDIUM)

**What:** OAuth2 client credentials for Microsoft Graph API (calendar, mail, tasks).
**Where used:** `G_Lists_Agent/.env`, `G_TaskCenter/.env`

### Steps

1. Go to [https://portal.azure.com](https://portal.azure.com).
2. Navigate to **Azure Active Directory** > **App registrations** > **+ New registration**.
3. Configure:
   - **Name:** `GEN_OS Integration`
   - **Supported account types:** Single tenant (this organization only)
   - **Redirect URI:** `http://localhost:3000/auth/callback` (Web)
4. Click **Register**.
5. From the **Overview** page, copy:
   - **Application (client) ID**
   - **Directory (tenant) ID**
6. Go to **Certificates & secrets** > **+ New client secret**:
   - Description: `gen-os-secret`
   - Expires: 24 months
   - Copy the **Value** immediately (shown only once).
7. Go to **API permissions** > **+ Add a permission** > **Microsoft Graph**:
   - Delegated permissions: `User.Read`, `Calendars.ReadWrite`, `Mail.Read`, `Tasks.ReadWrite`
   - Click **Grant admin consent** (if you have admin rights).
8. Update `.env` files:

```bash
# G_Lists_Agent/.env
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# G_TaskCenter/.env
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Verification

```bash
curl -s -X POST "https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token" \
  -d "client_id=<client-id>&scope=https://graph.microsoft.com/.default&client_secret=<secret>&grant_type=client_credentials"
# Expected: JSON with access_token
```

---

## 4. Gmail OAuth for G_TaskCenter (MEDIUM)

**What:** OAuth2 credentials for Gmail API (send/read emails from G_TaskCenter).
**Where used:** `G_TaskCenter/.env`

### Steps

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com).
2. Select or create a project (e.g., `gen-os-integration`).
3. Navigate to **APIs & Services** > **Enabled APIs** > Enable **Gmail API**.
4. Go to **APIs & Services** > **Credentials** > **+ Create Credentials** > **OAuth client ID**.
5. If prompted, configure the OAuth consent screen first:
   - **App name:** `GEN_OS TaskCenter`
   - **User support email:** your email
   - **Scopes:** `gmail.readonly`, `gmail.send`, `gmail.modify`
   - **Test users:** add your Gmail address
6. Back in Credentials, create OAuth client:
   - **Application type:** Desktop app (or Web if using redirect)
   - **Name:** `G_TaskCenter`
7. Download the `credentials.json` file.
8. Run the OAuth flow to obtain refresh token:

```bash
# Using the Google Auth library (Python)
pip install google-auth-oauthlib google-api-python-client
python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/gmail.modify']
)
creds = flow.run_local_server(port=0)
print(f'Refresh token: {creds.refresh_token}')
print(f'Client ID: {creds.client_id}')
print(f'Client secret: {creds.client_secret}')
"
```

9. Update `.env`:

```bash
# G_TaskCenter/.env
GMAIL_CLIENT_ID=xxxxxxxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_REFRESH_TOKEN=1//xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_USER_EMAIL=your.email@gmail.com
```

### Verification

```bash
curl -s "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=<access-token>"
# Expected: JSON with scope and email info
```

---

## 5. Tailscale VPN Configuration (MEDIUM)

**What:** Auth key for Tailscale VPN mesh network (optional but recommended for secure VM access).
**Where used:** `G_SV_Agent/.env`

### Steps

1. Go to [https://login.tailscale.com/admin/settings/keys](https://login.tailscale.com/admin/settings/keys).
2. Click **Generate auth key**.
3. Configure:
   - **Reusable:** Yes (for multiple devices)
   - **Ephemeral:** No (for persistent nodes)
   - **Tags:** `tag:gen-os` (optional, for ACL management)
   - **Expiration:** 90 days
4. Copy the auth key (starts with `tskey-auth-`).
5. Update `.env`:

```bash
# G_SV_Agent/.env
TAILSCALE_AUTH_KEY=tskey-auth-xxxxxxxxxxxxxxxxxx
```

### Installing Tailscale on VM101

```bash
# SSH into VM101
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey=tskey-auth-xxxxxxxxxxxxxxxxxx
tailscale status  # Verify connection
```

### Verification

```bash
tailscale status
# Expected: Shows connected devices in the tailnet
```

---

## 6. Docker Desktop (Local Dev) (MEDIUM)

**What:** Docker Desktop must be running locally for local development containers.
**Where used:** Local development environment

### Steps

1. Install Docker Desktop from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/).
2. Start Docker Desktop.
3. Verify installation:

```bash
docker version
docker compose version
```

4. Start local services:

```bash
cd c:/_Gen_OS/G_SV_Agent
make up
# or
docker compose up -d
```

### Verification

```bash
docker ps
# Expected: Running containers for local dev services
```

---

## Quick Reference: All Environment Variables

| Variable | Source | Used By |
|----------|--------|---------|
| `LANGFUSE_PUBLIC_KEY` | app.langfuse.com | GEN_OS-master, G_DeepResearch |
| `LANGFUSE_SECRET_KEY` | app.langfuse.com | GEN_OS-master, G_DeepResearch |
| `NOTION_TOKEN` | notion.so/my-integrations | G_Desktop, G_TaskCenter |
| `NOTION_DATABASE_ID` | Notion database URL | G_TaskCenter |
| `AZURE_CLIENT_ID` | portal.azure.com | G_Lists_Agent, G_TaskCenter |
| `AZURE_TENANT_ID` | portal.azure.com | G_Lists_Agent, G_TaskCenter |
| `AZURE_CLIENT_SECRET` | portal.azure.com | G_Lists_Agent, G_TaskCenter |
| `GMAIL_CLIENT_ID` | console.cloud.google.com | G_TaskCenter |
| `GMAIL_CLIENT_SECRET` | console.cloud.google.com | G_TaskCenter |
| `GMAIL_REFRESH_TOKEN` | OAuth flow | G_TaskCenter |
| `TAILSCALE_AUTH_KEY` | login.tailscale.com | G_SV_Agent |
| `PORTAINER_ADMIN_PASSWORD` | Self-set | G_SV_Agent (init script) |
