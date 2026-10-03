# SmartMed

AI-powered Pharmacy Inventory and Expiry Management System.

## Current Features

* User registration
* Secure password hashing
* JWT authentication
* Add medicines
* View all medicines
* Search medicines
* Update medicine quantity
* Delete medicines
* Detect low-stock medicines
* Detect expired medicines
* Detect medicines expiring within 30 days
* Medicine expiry status
* Dashboard summary
* PostgreSQL database integration

## Tech Stack

* Python
* FastAPI
* Pydantic
* PostgreSQL
* Psycopg2
* JWT
* Passlib / Bcrypt
* HTML, CSS and JavaScript *(upcoming frontend)*

## Project Structure

```text
SmartMed/
│
├── main.py
├── database.py
├── requirements.txt
├── .env
├── .gitignore
└── venv/
```

## API Features

### Authentication

* Register user
* Login user
* Generate JWT token
* Verify JWT token
* Protect medicine APIs

### Medicine Management

* Add medicine
* View all medicines
* Search medicine
* Update quantity
* Delete medicine

### Inventory Management

* Low-stock detection
* Expired medicine detection
* Expiring-soon detection
* Expiry status

### Dashboard

* Total medicines
* Low-stock count
* Expired medicine count
* Expiring-soon count

## Upcoming Features

* HTML/CSS/JavaScript Frontend
* Barcode Scanner Support
* OCR Integration
* Medicine image upload
* Advanced dashboard
* Docker Deployment
* Flutter Mobile Application
* Redis / background processing

## Database

SmartMed currently uses PostgreSQL for permanent medicine and user data storage.

## Future Vision

SmartMed aims to reduce manual pharmacy inventory work by combining medicine inventory management, expiry tracking, barcode scanning and OCR-based medicine information extraction.
