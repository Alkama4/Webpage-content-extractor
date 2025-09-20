## How to Run

### 1. Create & activate virtualenv
```bash
# Open terminal in backend folder
cd .\backend\

# Create a virtual enviroment
python -m venv venv

# Activate virtual enviroment
venv\Scripts\activate
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Add database credentils
Create a copy of the `.env.example` file inside the `backend/app` directory, rename it to `.env.local`, and then edit this new file to include your database connection details.

### 4. Start development server
```
uvicorn app.main:app --reload --port 8000
```

### 5. Open API docs
- Manual requests -> [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger UI -> [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc -> [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)