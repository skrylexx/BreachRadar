# GitHub Actions Snippets for BreachRadar

## 1. UV Setup (Python)
```yaml
      - name: ⚡ Install uv
        uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true
          version: "latest"

      - name: 🐍 Set up Python
        run: uv python install 3.12
```

## 2. Dependency Export & Audit
```yaml
      - name: 🐍 Backend Audit (pip-audit)
        run: |
          cd backend
          uv export --format requirements-txt > req.txt
          uvx pip-audit -r req.txt
```

## 3. Frontend Build with Environment Variables
```yaml
      - name: 🏗️ Build Check
        run: cd frontend && npm run build
        env:
          NEXT_PUBLIC_API_URL: "http://localhost:8000"
          NEXT_PUBLIC_TARGET_DOMAIN: "example.com"
          TARGET_DOMAIN: "example.com"
```

## 4. Docker Build Verification
```yaml
      - name: 🏗️ Build Backend Image
        run: docker build -t breachradar-api-test ./backend
```
