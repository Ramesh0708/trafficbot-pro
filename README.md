# 🚦 TrafficBot Pro  
Automated city traffic alerts posted directly into Microsoft Teams using GitHub Actions.

## Features
- Fetches latest local traffic news
- Smart one-line summary
- Live Google Maps traffic link
- Rotating trivia (50+ items)
- Multi-city support
- 100% automated (GitHub Actions free tier)
- No servers, no APIs, no hosting

## Usage

```yaml
name: TrafficBot Pro

on:
  schedule:
    - cron: "0 3 * * *"     # 8:30 AM IST
  workflow_dispatch:

jobs:
  trafficbot:
    runs-on: ubuntu-latest
    steps:
      - name: Run TrafficBot Pro
        uses: Ramesh0708/trafficbot-pro@v1
        with:
          city: "Pune"
          webhook: ${{ secrets.TEAMS_WEBHOOK_URL }}
