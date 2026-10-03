from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from database import get_connection
from datetime import date, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer


# FastAPI App Initialization
app = FastAPI()

load_dotenv()
# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


# JWT Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# Medicine Model
class Medicine(BaseModel):
    medicine_name: str
    quantity: int
    manufacturer: str
    expiry_date: str
    batch_number: str
    buying_price: float
    selling_price: float


# User Model
class User(BaseModel):
    username: str
    password: str


# Verify JWT Token
def verify_token(token: str = Depends(oauth2_scheme)):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("username")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return username

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# Register User
@app.post("/register")
def register(user: User):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check if username already exists
        cursor.execute(
            "SELECT id FROM users WHERE username = %s",
            (user.username,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        # Hash password
        hashed_password = pwd_context.hash(user.password)

        # Insert user
        query = """
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        """

        cursor.execute(
            query,
            (user.username, hashed_password)
        )

        connection.commit()

        return {
            "message": "User registered successfully"
        }

    except HTTPException:

        connection.rollback()
        raise

    except Exception as e:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        cursor.close()
        connection.close()


# Login User
@app.post("/login")
def login(user: User):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT id, username, password
    FROM users
    WHERE username = %s
    """

    cursor.execute(
        query,
        (user.username,)
    )

    existing_user = cursor.fetchone()

    cursor.close()
    connection.close()

    # Check if user exists
    if not existing_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Check password
    password_correct = pwd_context.verify(
        user.password,
        existing_user[2]
    )

    if not password_correct:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Create JWT token
    token = jwt.encode(
        {
            "user_id": existing_user[0],
            "username": existing_user[1]
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Login successful",
        "access_token": token
    }


# Add Medicine
@app.post("/add-medicine")
def add_medicine(
    medicine: Medicine,
    username: str = Depends(verify_token)
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO medicines (
        medicine_name,
        quantity,
        manufacturer,
        expiry_date,
        batch_number,
        buying_price,
        selling_price
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        medicine.medicine_name,
        medicine.quantity,
        medicine.manufacturer,
        medicine.expiry_date,
        medicine.batch_number,
        medicine.buying_price,
        medicine.selling_price
    )

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Medicine added successfully!"
    }


# Get All Medicines
@app.get("/all-medicines")
def get_all_medicines(
    username: str = Depends(verify_token)
):

    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM medicines"

    cursor.execute(query)

    medicines = cursor.fetchall()

    cursor.close()
    connection.close()

    return medicines


# Search Medicine
@app.get("/search-medicine")
def search_medicine(
    name: str,
    username: str = Depends(verify_token)
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT * FROM medicines
    WHERE medicine_name = %s
    """

    cursor.execute(
        query,
        (name,)
    )

    medicine = cursor.fetchone()

    cursor.close()
    connection.close()

    if medicine:

        return medicine

    return {
        "message": "Medicine not found."
    }


# Update Medicine Quantity
@app.put("/update-quantity")
def update_quantity(
    name: str,
    quantity: int,
    username: str = Depends(verify_token)
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    UPDATE medicines
    SET quantity = %s
    WHERE medicine_name = %s
    """

    cursor.execute(
        query,
        (quantity, name)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Quantity updated successfully!"
    }


# Delete Medicine
@app.delete("/delete-medicine")
def delete_medicine(
    name: str,
    username: str = Depends(verify_token)
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    DELETE FROM medicines
    WHERE medicine_name = %s
    """

    cursor.execute(
        query,
        (name,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Medicine deleted successfully!"
    }


# Check Low Stock Medicines
@app.get("/low-stock")
def low_stock(
    username: str = Depends(verify_token)
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT * FROM medicines
    WHERE quantity < 10
    """

    cursor.execute(query)

    medicines = cursor.fetchall()

    cursor.close()
    connection.close()

    return medicines


# Check Medicines Expiring Within 30 Days
@app.get("/expiring-soon")
def expiring_soon(
    username: str = Depends(verify_token)
):

    connection = get_connection()
    cursor = connection.cursor()

    today = date.today()

    future_date = today + timedelta(days=30)

    query = """
    SELECT * FROM medicines
    WHERE expiry_date >= %s
    AND expiry_date <= %s
    """

    cursor.execute(
        query,
        (today, future_date)
    )

    medicines = cursor.fetchall()

    cursor.close()
    connection.close()

    return medicines


# Check Medicine Expiry Status
@app.get("/expiry-status")
def expiry_status(
    username: str = Depends(verify_token)
):

    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM medicines"

    cursor.execute(query)

    medicines = cursor.fetchall()

    cursor.close()
    connection.close()

    result = []

    today = date.today()

    for medicine in medicines:

        expiry_date = medicine[4]

        if expiry_date < today:

            status = "Expired"

        elif expiry_date <= today + timedelta(days=30):

            status = "Expiring Soon"

        else:

            status = "Safe"

        result.append({
            "medicine": medicine[1],
            "expiry_date": expiry_date,
            "status": status
        })

    return result


# SmartMed Dashboard Summary
@app.get("/dashboard-summary")
def dashboard_summary(
    username: str = Depends(verify_token)
):

    connection = get_connection()
    cursor = connection.cursor()

    # Total medicines
    cursor.execute(
        "SELECT COUNT(*) FROM medicines"
    )

    total_medicines = cursor.fetchone()[0]

    # Low stock
    cursor.execute("""
        SELECT COUNT(*) FROM medicines
        WHERE quantity < 10
    """)

    low_stock = cursor.fetchone()[0]

    # Expired
    cursor.execute("""
        SELECT COUNT(*) FROM medicines
        WHERE expiry_date < CURRENT_DATE
    """)

    expired = cursor.fetchone()[0]

    # Expiring within 30 days
    cursor.execute("""
        SELECT COUNT(*) FROM medicines
        WHERE expiry_date >= CURRENT_DATE
        AND expiry_date <= CURRENT_DATE + INTERVAL '30 days'
    """)

    expiring_soon = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return {
        "total_medicines": total_medicines,
        "low_stock": low_stock,
        "expired": expired,
        "expiring_soon": expiring_soon
    }