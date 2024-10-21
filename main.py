#Importing required packages
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import psycopg2
from pydantic import BaseModel, EmailStr, model_validator, field_validator
import pandas as pd
from io import StringIO

app = FastAPI() #Initializing FastAPI

# Database connection setup
conn = psycopg2.connect(
    dbname='ADD YOUR DBNAME',#Change it to your DB Name
    user='ADD YOUR USERNAME',#Change it to your UserName
    password='ADD YOUR DB PASSWORD',#Change it to your Password
    host='ADD YOUR HOST',#Change it to your host. If you are hosting it locally it'll be localhost
    port='PORT'#Change it to your port. If you are hosting it locally it'll be 5432
)
c = conn.cursor()

# Ensure tables exist and creating if it doesn't
c.execute("""CREATE TABLE IF NOT EXISTS data (
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) PRIMARY KEY UNIQUE NOT NULL,
        phn_num VARCHAR(15) UNIQUE NOT NULL);
""")

c.execute("""CREATE TABLE IF NOT EXISTS expenses (
        expense_id SERIAL,
        amount FLOAT NOT NULL,
        email VARCHAR(100) REFERENCES data(email) ON DELETE CASCADE
    );
""")

# Pydantic model classes 
class AddUser(BaseModel):
    name: str
    email: EmailStr
    phn_num: str

class AddExpense(BaseModel):
    email: EmailStr
    amt: float

class SplitEqual(BaseModel):
    email: list[EmailStr]
    totalamt: float

class SplitExact(BaseModel):
    email: list[EmailStr]
    amts: list[float]
    
    #Validators to check if the number of entries are equal
    @model_validator(mode='before')
    def check_equal_length(cls, values):
        emails = values.get('email')
        exactamts = values.get('amts')
        
        if len(emails) != len(exactamts):
            raise ValueError('The number of entries must be same')
        return values

class SplitPercent(BaseModel):
    email: list[EmailStr]
    total: float
    percent: list[int]

    #Validator to check if the percentages add up to 100
    @field_validator('percent')
    def validate_percent(cls, v):
        if sum(v) != 100:
            raise ValueError('The total must sum up to 100')
        return v

    @model_validator(mode='before')
    def check_equal_length(cls, values):
        emails = values.get('email')
        percents = values.get('percent')
        
        if len(emails) != len(percents):
            raise ValueError('The number of entries must be same.')
        return values

# API Routes

#Home Route
@app.get("/")
async def home():
    return {"200": "OK"}

#Add User Route
@app.post("/users/")
async def adduser(user: AddUser):
    try:
        c.execute("INSERT INTO data(name, email, phn_num) VALUES(%s, %s, %s);", (user.name, user.email, user.phn_num))
        conn.commit()
        return {"status": "Success", "data": user}
    except Exception as e: 
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#User Details Route
@app.get("/users/{name}")
async def user_details(name: str):
    try:
        c.execute("SELECT * FROM data WHERE name= %s;", (name,))
        details = c.fetchall()
        if not details:
            raise HTTPException(status_code=404, detail="User not found")
        return details
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#Add Expense Route
@app.post("/expense/")
async def add_expense(user: AddExpense):
    try:
        c.execute("SELECT * FROM data WHERE email = %s;", (user.email,))
        if not c.fetchone():
            raise HTTPException(status_code=404, detail="User does not exist")
        
        # Insert expense as a float value
        c.execute("INSERT INTO expenses (amount, email) VALUES (%s, %s);", (user.amt, user.email))
        conn.commit()
        return {"status": "Success", "expense": {"email": user.email, "amount": user.amt}}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#Expenses of a particular user
@app.get("/expense/user/{email}")
async def user_expenses(email: str):
    try:
        c.execute("SELECT amount FROM expenses WHERE email = %s;", (email,))
        details = c.fetchall()
        if not details:
            raise HTTPException(status_code=404, detail="User has no expenses")
        return details
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#All Expenses
@app.get("/expense/all")
async def all_expenses():
    try:
        c.execute("SELECT * FROM expenses")
        details = c.fetchall()
        return details
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#Balance sheet download
@app.get("/expense/download/{email}")
async def balsheet(email: str):
    try:
        c.execute("SELECT amount FROM expenses WHERE email = %s;", (email,))
        exp = c.fetchall()
        if not exp:
            return {"status": "No expenses found"}
        allexp = [{"amount": entry[0]} for entry in exp]
        df = pd.DataFrame(allexp)
        csv = StringIO()
        df.to_csv(csv, index=False)
        csv.seek(0)

        return StreamingResponse(
            csv, 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=balsheet.csv"}
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#Splitting equally Route
@app.post("/expense/split/equal")
async def split_equal(exp: SplitEqual):
    try:
        amt = exp.totalamt / len(exp.email)
        for email in exp.email:
            c.execute("INSERT INTO expenses(amount, email) VALUES (%s, %s);", (amt, email))
        conn.commit()
        return {"status": "Success", "split_amount": amt, "total": exp.totalamt, "emails": exp.email}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#Splitting Exact Route
@app.post("/expense/split/exact")
async def split_exact(exp: SplitExact):
    try:
        for email, amount in zip(exp.email, exp.amts):
            c.execute("INSERT INTO expenses(amount, email) VALUES (%s, %s);", (amount, email))
        conn.commit()
        return {"status": "Success"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#Splitting by Percentage Route
@app.post("/expense/split/percentage")
async def split_percent(exp: SplitPercent):
    try:
        amounts = [(percent / 100) * exp.total for percent in exp.percent]
        for email, amount in zip(exp.email, amounts):
            c.execute("INSERT INTO expenses(amount, email) VALUES (%s, %s);", (amount, email))
        conn.commit()
        return {"status": "Success"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
