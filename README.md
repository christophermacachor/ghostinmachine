# 1. Install Fly CLI (once)
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Create app (once)
fly apps create omega-swarm-macos

# 4. Deploy
fly deploy

# 5. Check logs (live)
fly logs

# 6. Open in browser
fly open
