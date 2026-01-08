# Ecommerce Backend

**Full-stack ecommerce application – Backend**

This backend is built using **Django REST Framework** and **MySQL**.  
It provides APIs for products, cart, orders, and user authentication.

---

## Features
- Product management (add/update/delete)
- Cart & order handling
- User authentication with JWT
- Stores order history in database
- Admin can manage products
- CORS enabled for frontend integration

---

## Tech Stack
- **Backend:** Django, Django REST Framework, Simple JWT, CORS Headers
- **Database:** MySQL
- **Environment Variables:** python-dotenv

---

## Installation (Local)
```bash
cd ecommerce-backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
