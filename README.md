# E2EE Drive - FastAPI Backend (Google ID Token auth)

## Quick start

1. Create a virtualenv and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set environment variables (recommended):
```bash
export GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
export DATABASE_URL=sqlite:///./e2ee_drive.db
```

3. Run the app:
```bash
uvicorn main:app --reload --port 8000
```

4. The API endpoints:
- `POST /folders`  - create folder (requires Authorization: Bearer <id_token>)
- `GET /folders`   - list child folders (requires Authorization)
- `GET /folders/all` - list all user folders (requires Authorization)

## Notes
- This backend verifies Google ID tokens using `google-auth` library.
- CORS is configured to allow `http://localhost:3000` and the Authorization header.
