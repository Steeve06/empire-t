# Deploy on Oracle Cloud (free)

Oracle Cloud's **Always Free** tier includes an ARM server that runs this project at no cost. Allow about 30 minutes, most of it waiting. CI starts the full production stack on ARM on every push, so the images are known to work on it.

You need a credit or debit card for Oracle's identity check. Always Free resources are not charged.

## 1. Create the account

1. Sign up at <https://www.oracle.com/cloud/free/>.
2. **Home region:** choose **Germany Central (Frankfurt)** or **France Central (Paris)**. This cannot be changed later, and Europe gives Yaoundé the lowest latency.
3. Recommended once the account is active: **Billing › Upgrade and Manage Payment › Pay As You Go**. You still pay nothing within the Always Free limits, and Oracle no longer reclaims "idle" free servers, which a new site with little traffic can look like.

## 2. Create the server

**Menu › Compute › Instances › Create instance**

| Setting | Value |
|---|---|
| Name | `empire-t` |
| Image | **Canonical Ubuntu 24.04** (click *Change image*) |
| Shape | *Change shape* › **Ampere** › **VM.Standard.A1.Flex**, **2 OCPUs**, **12 GB** memory |
| Networking | Keep the defaults: new virtual cloud network, **public subnet**, *Assign a public IPv4 address* checked |
| SSH keys | **Generate a key pair for me** › **Save private key**. Keep this file safe: it is the only way in. |
| Boot volume | Default (about 47 GB) is enough |

Click **Create**. When the state turns green (*Running*), copy the **Public IP address**.

> **"Out of capacity for shape VM.Standard.A1.Flex"** is common. Try another *Availability domain* in the placement section, retry a few hours later, or choose 1 OCPU and 6 GB. As a last resort, **VM.Standard.E2.1.Micro** (AMD, 1 GB, also free) works: the setup script adds swap memory, but the first build is slow.

## 3. Open the web ports in Oracle's network

Oracle blocks everything except SSH by default.

1. On the instance page, click the **subnet** link, then the **Default Security List**.
2. **Add Ingress Rules**, twice:

| Source CIDR | IP protocol | Destination port |
|---|---|---|
| `0.0.0.0/0` | TCP | `80` |
| `0.0.0.0/0` | TCP | `443` |

The setup script opens the same ports in the server's own firewall.

## 4. Connect from Windows

In PowerShell, using the key file you saved and the public IP:

```powershell
# Once: Windows SSH refuses a key that other accounts can read
$key = "$HOME\Downloads\ssh-key-2026-11-03.key"     # your file name
icacls $key /inheritance:r
icacls $key /grant:r "$($env:USERNAME):(R)"

ssh -i $key ubuntu@YOUR-PUBLIC-IP
```

Answer `yes` the first time. The prompt becomes `ubuntu@empire-t:~$`.

## 5. Install everything (one command)

```bash
curl -fsSL https://raw.githubusercontent.com/Steeve06/empire-t/main/infra/scripts/server-setup.sh \
  | sudo bash -s -- --email you@example.com
```

Use a real email address: Let's Encrypt writes to it before the certificate expires. Add `--domain your-domain.com` if you already have a domain pointing at the server (see the [deployment guide](deployment.md#2-domain)). Without one, the site gets a free address built from the IP: `https://203-0-113-10.sslip.io`.

The script prints each step. The first build takes 10 to 20 minutes on the free server. It ends with:

```
Empire T is online.
  Site:   https://203-0-113-10.sslip.io/fr/
  Admin:  https://203-0-113-10.sslip.io/admin/
          user: admin   password: ...
```

Open the site on your phone and share the link.

## 6. Right after

1. Log in to the admin and **change the password** (top right).
2. **Admin › Paramètres du site:** check the WhatsApp number (test bookings go there), the email, the map pin.
3. **Nightly backup:** run `crontab -e` and add
   `15 3 * * * cd /srv/empire-t && infra/scripts/backup.sh >> /srv/empire-t/backups/backup.log 2>&1`
4. Optional: Oracle offers 20 GB of free Object Storage. With rclone, it can hold an off-site copy of the backups ([deployment guide, section 6](deployment.md#6-backups)).

## Updating later

From the second login on, the `ubuntu` user runs Docker without `sudo`.

```bash
ssh -i $key ubuntu@YOUR-PUBLIC-IP
cd /srv/empire-t && make prod-deploy
```

## Moving to a real domain

Point the domain at the server ([deployment guide, section 2](deployment.md#2-domain)), then run the setup command again with `--domain your-domain.com`. It keeps the database, photos and passwords, requests a new certificate and re-renders the pages.

## If something goes wrong

| Symptom | Fix |
|---|---|
| `ssh: connect ... timed out` | Wrong IP, or the instance is not *Running* |
| `Permissions for '...key' are too open` | Run the two `icacls` lines in step 4 again |
| Certificate step fails with a timeout | Step 3 is missing: ports 80 and 443 must be open in the security list |
| Certificate step fails with `too many certificates already issued` | Let's Encrypt's weekly limit for the shared `sslip.io` name. Retry in a few days, or use a free `duckdns.org` name or your own domain with `--domain` |
| Build stops or the server freezes | Too little memory (Micro shape): run the setup command again, as swap is now active |
| `permission denied ... docker.sock` | Log out and back in once after the setup (the `ubuntu` user was added to the `docker` group) |
| Anything else | `cd /srv/empire-t && make prod-logs`, then send the last lines |
