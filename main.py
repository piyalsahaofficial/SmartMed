from fastapi import FastAPI
from pydantic import BaseModel

# FastAPI App Initialization
app = FastAPI()

# Temporary Storage (Will be replaced by PostgreSQL later)
medicine_inventory = []


# Medicine Model
class Medicine(BaseModel):
    medicine_name: str
    quantity: int
    manufacturer: str
    expiry_date: str
    batch_number: str
    buying_price: float
    selling_price: float


# Add a Medicine
@app.post("/add-medicine")
def add_medicine(medicine: Medicine):
    medicine_inventory.append(medicine)
    return {
        "message": "Medicine added successfully!"
    }


# View All Medicines
@app.get("/all-medicines")
def get_all_medicines():
    return medicine_inventory


# Search Medicine by Name
@app.get("/search-medicine")
def search_medicine(name: str):

    for medicine in medicine_inventory:
        if medicine.medicine_name == name:
            return medicine

    return {
        "message": "Medicine not found."
    }


# Update Medicine Quantity
@app.put("/update-quantity")
def update_quantity(name: str, quantity: int):

    for medicine in medicine_inventory:
        if medicine.medicine_name == name:
            medicine.quantity = quantity

            return {
                "message": "Quantity updated successfully!"
            }

    return {
        "message": "Medicine not found."
    }


# Delete Medicine
@app.delete("/delete-medicine")
def delete_medicine(name: str):

    for medicine in medicine_inventory:
        if medicine.medicine_name == name:
            medicine_inventory.remove(medicine)

            return {
                "message": "Medicine deleted successfully!"
            }

    return {
        "message": "Medicine not found."
    }


# Check Low Stock Medicines
@app.get("/low-stock")
def low_stock():

    low_stock_medicines = []

    for medicine in medicine_inventory:
        if medicine.quantity < 10:
            low_stock_medicines.append(medicine)

    return low_stock_medicines