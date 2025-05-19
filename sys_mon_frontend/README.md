# sys_mon_frontend

This is the admin dashboard frontend for sys_mon, built with Vite, React, and TypeScript.

## Features
- Lists all reporting machines
- Displays latest values from each
- Flags configuration issues (e.g., unencrypted disk, outdated OS)
- Shows last check-in time
- Provides filters/sorting (by OS, status)

## Getting Started

1. Install dependencies:
   ```sh
   npm install
   ```
2. Start the development server:
   ```sh
   npm run dev
   ```
3. The app will be available at http://localhost:5173

## API
This frontend expects the sys_mon_server FastAPI backend to be running and accessible. Update API endpoints in the code as needed.
