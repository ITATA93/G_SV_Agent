---
depends_on:
  - configs/services.yml
impacts:
  - docs/SERVICE_CATALOG.md
---

# Operations Guide — G_SV_Agent

> Last updated: 2026-03-02
> Service count: 24 (see `docs/SERVICE_CATALOG.md`)

## Infrastructure Overview

| Component | Address | Role |
|-----------|---------|------|
| Proxmox Host | 65.21.233.178 | Bare-metal hypervisor (AMD EPYC 7502P, 128GB RAM) |
| VM100 (dev) | 10.10.10.100 | AI stack: Ollama, Qdrant, Open WebUI |
| VM101 (services) | 10.10.10.101 | Docker services: 22 containers |
| Cloudflare Tunnel | sv-hetzner | Reverse proxy for all *.imedicina.cl domains |

## SSH Access

All remote operations use a jump host pattern through Proxmox:

```bash
# Option 1: Direct SSH (requires network access to Hetzner)
ssh root@65.21.233.178
ssh matias@10.10.10.101  # from Proxmox host

# Option 2: Via Cloudflare tunnel (from anywhere)
cloudflared access tcp --hostname ssh-hetzner.imedicina.cl --url localhost:2222
ssh root@localhost -p 2222  # then jump to VM101
```

Scripts use the jump host pattern automatically:
```bash
ssh root@65.21.233.178 "ssh matias@10.10.10.101 '<command>'"
```

## Service Lifecycle

### Check all services
```bash
bash scripts/verify-services.sh
```

### Deploy missing services
```bash
bash scripts/deploy-vm101-services.sh --dry-run  # preview
bash scripts/deploy-vm101-services.sh             # execute
```

### Restart a specific container (via SSH)
```bash
ssh root@65.21.233.178 "ssh matias@10.10.10.101 'docker restart <container-name>'"
```

### View logs
```bash
ssh root@65.21.233.178 "ssh matias@10.10.10.101 'docker logs --tail 50 <container-name>'"
```

### Fix Prometheus
```bash
bash scripts/fix_prometheus.sh --dry-run
bash scripts/fix_prometheus.sh
```

### Reset Portainer admin
```bash
bash scripts/init_portainer.sh --dry-run
bash scripts/init_portainer.sh
```

## Adding a New Service

**This is the mandatory procedure for registering new services:**

1. **Edit `configs/services.yml`** — add the service entry with all fields
2. **Run sync**: `python scripts/sync_service_catalog.py`
   - This regenerates `scripts/verify-services.sh` and `docs/SERVICE_CATALOG.md`
3. **Update `.env`** — add any new credentials/URLs
4. **Update `.env.example`** — add placeholder entries
5. **Commit** all generated + modified files

If deploying via Docker on VM101, also update `scripts/deploy-vm101-services.sh` if the service needs special setup (databases, env files, etc.).

## Removing a Service

1. **Edit `configs/services.yml`** — set `deployed: false` or remove the entry
2. **Run sync**: `python scripts/sync_service_catalog.py`
3. **Stop the container** on VM101: `docker stop <container> && docker rm <container>`
4. **Clean up `.env`** if credentials are no longer needed
5. **Commit** changes

## Recovery Playbook (502 Errors)

When services return 502 via Cloudflare tunnel:

1. **Check tunnel status**:
   ```bash
   curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/cfd_tunnel/$CLOUDFLARE_TUNNEL_ID" \
     | python -m json.tool
   ```

2. **Check VM status via Proxmox API**:
   ```bash
   curl -sk "https://65.21.233.178:8006/api2/json/nodes/antigravity-core/qemu" \
     -H "Authorization: PVEAPIToken=$PROXMOX_TOKEN"
   ```
   Look for `qmpstatus: io-error` — indicates disk I/O freeze.

3. **If io-error — check disk space on host**:
   ```bash
   ssh root@65.21.233.178 "df -h /"
   ```

4. **Clean disk if needed**:
   ```bash
   # On Proxmox host:
   journalctl --vacuum-size=100M
   apt clean
   rm -f /var/lib/vz/template/iso/*.iso  # old ISOs
   ```

5. **Resume frozen VMs**:
   ```bash
   # Via Proxmox API — QEMU monitor 'cont' command:
   curl -sk -X POST "https://65.21.233.178:8006/api2/json/nodes/antigravity-core/qemu/101/monitor" \
     -H "Authorization: PVEAPIToken=$PROXMOX_TOKEN" \
     -d "command=cont"
   ```

6. **Verify services**:
   ```bash
   bash scripts/verify-services.sh
   ```

## Disk Space Management

- **Filesystem**: XFS (use `xfs_growfs /`, NOT `resize2fs`)
- **Current**: 500GB allocated from 892GB VG, ~384GB free for expansion
- **Watchdog**: `/usr/local/bin/disk-watchdog.sh` runs every 30min, cleans if >90%
- **Journal limit**: 100MB max via `/etc/systemd/journald.conf.d/size-limit.conf`

## Monitoring

| Tool | URL | Purpose |
|------|-----|---------|
| Grafana | https://grafana.imedicina.cl | Metrics dashboards |
| Prometheus | https://prometheus.imedicina.cl | Metrics collection |
| Uptime Kuma | https://uptime.imedicina.cl | Uptime monitoring |
| Dozzle | https://dozzle.imedicina.cl | Real-time Docker logs |
| Portainer | https://portainer.imedicina.cl | Container management |

## Firewall Rules (Proxmox Host)

| Port | Service | Status |
|------|---------|--------|
| 22 | SSH | Allowed |
| 80 | HTTP | Allowed |
| 443 | HTTPS | Allowed |
| 8006 | Proxmox UI | Allowed |
| 3128 | SPICE | Allowed |
| 111 | rpcbind | Blocked (masked) |
| * | All other inbound | DROP (ctstate NEW on vmbr0) |

## Scripts Registry

See `docs/library/scripts.md` for the full list of automation scripts with usage instructions.
