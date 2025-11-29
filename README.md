# 🚦 TrafficBot Pro  
Automated city traffic alerts delivered to Microsoft Teams using GitHub Actions.

## 📌 Features
- Multi-city traffic updates  
- AI-style one-line summaries  
- Severity markers  
- Google Maps live traffic  
- Rotating fun facts (50+ items)  
- Fully automated on schedule  
- Zero server cost (runs on GitHub Actions)

## 📌 Example Workflow

```yaml
name: TrafficBot Pro

on:
  schedule:
    - cron: "0 3 * * *"      # 8:30 AM IST
  workflow_dispatch:

jobs:
  traffic:
    runs-on: ubuntu-latest
    steps:
      - name: Run TrafficBot Pro
        uses: Ramesh0708/trafficbot-pro@v1
        with:
          city: "Pune"
          webhook: ${{ secrets.TEAMS_WEBHOOK_URL }}
