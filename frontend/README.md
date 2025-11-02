# NRRC Arabic PoV - Frontend

Modern Arabic RTL interface for the document retrieval system.

## Structure

```
frontend/
└── index.html    # Single-page application
```

## Features

- Beautiful Arabic RTL interface
- JWT-based authentication
- Role-based access control (RBAC)
- Real-time search with highlighting
- Responsive design
- Modern UI/UX

## Configuration

Update the API URL in `index.html`:

```javascript
const API_URL = 'https://your-render-backend-url.onrender.com';
```

## Deployment on Vercel

1. Push code to GitHub
2. Import repository in Vercel
3. Set Root Directory to `frontend`
4. Framework Preset: Other
5. Add environment variable:
   - `REACT_APP_API_URL`: Your backend URL

See `../deploy.txt` for detailed deployment instructions.

## Local Development

Simply open `index.html` in a browser or use a local server:

```bash
cd frontend
python -m http.server 3000
# or
npx serve .
```

Access at: http://localhost:3000

## Test Accounts

- **Admin**: `admin` / `admin123`
- **Legal**: `legal` / `legal123`
- **Staff**: `staff` / `staff123`

