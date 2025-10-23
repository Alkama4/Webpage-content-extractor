# Setup dev environment

## 1. Create & activate a virtual environment
```bash
# Open a terminal in the `backend` directory
cd backend/

# Create a virtual environment named `venv`
python -m venv venv

# Activate it
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux
```


## 2. Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Configure the database
1. Create a copy of the `.env.example` called `.env.local`.
2. Edit the `backend/app/.env.local` and set your database credentials (e.g., `DB_HOST`, `DB_USER`, etc.).


## 4. Run the development server
```bash
uvicorn app.main:app --reload --port 8000
```

## 5. Access the API & docs

| URL | What it shows |
|-----|---------------|
| <http://127.0.0.1:8000/docs> | Swagger UI (interactive docs, recommended) |
| <http://127.0.0.1:8000/redoc> | ReDoc (alternative docs) |
| <http://127.0.0.1:8000> | Make manual requests |


# All in one setup

After the initial setup you can just use the following to get the server up and running quick.

```bash
cd backend/
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```