# FastAPI Expense Tracker API Documentation

## Overview

This API allows you to manage user information and expenses with various features such as adding users, adding expenses, splitting expenses, and downloading expense records in CSV format.

## Features
- Add and manage users.
- Add expenses for users.
- Split expenses equally, by exact amounts, or by percentages among users.
- Download expense data in CSV format for any user.
- Integrated with PostgreSQL database.

---

## Requirements
To run the API, ensure that you have the following installed:
- **Python 3.8+**
- **PostgreSQL 9.6+**

### Required Python Packages
- `fastapi`
- `psycopg2`
- `pydantic`
- `pandas`
- `uvicorn`

---

## Installation Guide

### 1. Install Python Packages

First, clone the repository or download the code. Afterward, run the following command to install all required dependencies using `pip`:

```bash
pip install fastapi psycopg2 pandas uvicorn pydantic
```

Alternatively, you can create a `requirements.txt` file with the following content and run `pip install -r requirements.txt`:

```txt
fastapi
psycopg2
pandas
uvicorn
pydantic
```

### 2. Setup PostgreSQL Database

1. Install PostgreSQL and start the PostgreSQL server.
   - For **Linux**:
     ```bash
     sudo apt update
     sudo apt install postgresql postgresql-contrib
     ```
   - For **Mac** (using Homebrew):
     ```bash
     brew install postgresql
     ```

2. Create a new PostgreSQL database for this project:
   ```bash
   psql -U postgres
   CREATE DATABASE expense_tracker;
   ```

3. Create a new user and grant privileges:
   ```sql
   CREATE USER your_username WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO your_username;
   ```

4. Update the database connection details in the code:
   In the Python code, replace the placeholders in the `psycopg2.connect` section with your actual PostgreSQL connection details.

   ```python
   conn = psycopg2.connect(
       dbname='expense_tracker',   # Change to your DB name
       user='your_username',       # Change to your username
       password='your_password',   # Change to your password
       host='localhost',           # Change if hosted elsewhere
       port='5432'                 # Default PostgreSQL port
   )
   ```

---

## Running the API

After setting up the database and installing dependencies, you can run the FastAPI application using `uvicorn`. In the terminal, navigate to the project directory and run:

```bash
uvicorn main:app --reload
```

The `--reload` flag enables live reloading during development.

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Testing via Swagger UI

FastAPI provides an interactive interface using Swagger UI for testing the API. Access it at:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc** (alternative documentation): [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Access any one of the above and select the routes and click "Try it out". Then enter the required required body and click on execute to test the API.

### Testing Endpoints

1. **Home Route**: Verify the API is running:
   - `GET /`
   - Response: `{ "200": "OK" }`

2. **Add a User**: Add user information (name, email, phone number).
   - `POST /users/`
   - Example Request Body:
     ```json
     {
       "name": "John Doe",
       "email": "johndoe@example.com",
       "phn_num": "1234567890"
     }
     ```
   - Response: `{"status": "Success", "data": {...}}`

3. **View User Details**: Get user details by name.
   - `GET /users/{name}`
   - Response: `[{ "name": "John Doe", "email": "johndoe@example.com", ... }]`

4. **Add an Expense**: Add an expense to a specific user.
   - `POST /expense/`
   - Example Request Body:
     ```json
     {
       "email": "johndoe@example.com",
       "amt": 100.5
     }
     ```
   - Response: `{"status": "Success", "expense": {...}}`

5. **Get User's Expenses**: Retrieve all expenses for a particular user.
   - `GET /expense/user/{email}`
   - Response: `[{"amount": 100.5}, ...]`

6. **Get All Expenses**: Retrieve all expenses from the database.
   - `GET /expense/all`
   - Response: `[[1, 100.5, "johndoe@example.com"], ...]`

7. **Download Expense Sheet (CSV)**: Download user's expense data as a CSV file.
   - `GET /expense/download/{email}`
   - Response: CSV file.

8. **Split Expenses Equally**: Split the total amount equally among a list of users.
   - `POST /expense/split/equal`
   - Example Request Body:
     ```json
     {
       "email": ["johndoe@example.com", "janedoe@example.com"],
       "totalamt": 200.0
     }
     ```
   - Response: `{ "status": "Success", "split_amount": 100.0 }`

9. **Split Expenses Exactly**: Split a specified amount for each user.
   - `POST /expense/split/exact`
   - Example Request Body:
     ```json
     {
       "email": ["johndoe@example.com", "janedoe@example.com"],
       "amts": [120.5, 80.0]
     }
     ```
   - Response: `{"status": "Success"}`

10. **Split Expenses by Percentage**: Split the total amount based on specified percentages.
    - `POST /expense/split/percentage`
    - Example Request Body:
      ```json
      {
        "email": ["johndoe@example.com", "janedoe@example.com"],
        "total": 300.0,
        "percent": [60, 40]
      }
      ```
    - Response: `{"status": "Success"}`

---

## Notes

- Ensure PostgreSQL is running before starting the API.
- Replace placeholder values (like database credentials) with your actual information.
- You can test all endpoints easily using the **Swagger UI** and interactively explore the API's capabilities.

---
