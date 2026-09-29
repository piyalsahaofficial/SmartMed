
from fastapi import FastAPI
from pydantic import BaseModel
from database import get_connection
from datetime import date, timedelta


# FastAPI App Initialization
app = FastAPI()


# Medicine Model
class Medicine(BaseModel):
    medicine_name: str
    quantity: int
    manufacturer: str
    expiry_date: str
    batch_number: str
    buying_price: float
    selling_price: float


# Add Medicine
@app.post("/add-medicine")
def add_medicine(medicine: Medicine):

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
def get_all_medicines():

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
def search_medicine(name: str):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT * FROM medicines
    WHERE medicine_name = %s
    """

    cursor.execute(query, (name,))

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
def update_quantity(name: str, quantity: int):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    UPDATE medicines
    SET quantity = %s
    WHERE medicine_name = %s
    """

    values = (quantity, name)

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Quantity updated successfully!"
    }


# Delete Medicine
@app.delete("/delete-medicine")
def delete_medicine(name: str):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    DELETE FROM medicines
    WHERE medicine_name = %s
    """

    cursor.execute(query, (name,))
    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Medicine deleted successfully!"
    }


# Check Low Stock Medicines
@app.get("/low-stock")
def low_stock():

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
def expiring_soon():

    connection = get_connection()
    cursor = connection.cursor()

    today = date.today()
    future_date = today + timedelta(days=30)

    query = """
    SELECT * FROM medicines
    WHERE expiry_date >= %s
    AND expiry_date <= %s
    """

    cursor.execute(query, (today, future_date))

    medicines = cursor.fetchall()

    cursor.close()
    connection.close()

    return medicines

# Check Medicine Expiry Status
@app.get("/expiry-status")
def expiry_status():

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
def dashboard_summary():

    connection = get_connection()
    cursor = connection.cursor()

    # Total medicines
    cursor.execute("SELECT COUNT(*) FROM medicines")
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