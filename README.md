# Infra Visualizer

## Screenshot

![Demo](screenshots/demo.png)

Convert Terraform and Kubernetes files into architecture diagrams automatically.

## Features

- Terraform visualization
- Kubernetes YAML visualization
- AWS architecture grouping
- PNG export
- AI explanation

## Tech Stack

Frontend:
- React
- TypeScript
- React Flow
- Vite

Backend:
- FastAPI
- Python
- Terraform HCL parser

## Run Locally

### Backend

```bash
cd backend
uvicorn app:app --reload
```

### Frontend

```bash
cd frontend
npm run dev
```

## Demo

Upload:
- .tf files
- .yaml files

Generate:
- Architecture diagrams
- AI explanations