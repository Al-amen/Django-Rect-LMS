# 📘 Django-React-LMS

A full-stack **Learning Management System (LMS)** inspired by **Udemy**, built using **Django** and **React**. This platform allows instructors to create and sell courses while students can enroll, learn, and track their progress.

---

## 🔧 Tech Stack

- **Backend:** Django, Django REST Framework (DRF)
- **Frontend:** React.js, Axios
- **Database:** PostgreSQL
- **Authentication:** JWT or Django session-based auth
- **Payments:** Sripe, Paypal
- **Media Management:** Django `ImageField`, static/media files

---

## 🎯 Features

### 🧑‍🏫 For Teachers
- Create, update, delete courses  
- Upload video content and downloadable files  
- View student enrollment and feedback  

### 👨‍🎓 For Students
- Browse and enroll in courses  
- Track lesson completion  
- Post reviews and ratings after completing a course  

### 💳 Payment Integration
- Integrated SSLCommerz gateway for secure transactions  
- Order tracking, invoice downloads  

### ⭐ Reviews & Ratings
- Students can post detailed reviews and rate courses  
- Helps improve course quality and visibility  

### 🗂️ Dashboard
- Students: Track enrolled courses and progress  
- Teachers: Manage uploaded courses and see performance  
- Shipping/Order status (for physical or premium products if extended)

---

## 🚀 Installation

### Backend (Django)
```bash
git clone https://github.com/Al-amen/Django-Rect-LMS
cd Django-Rect-LMS/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

```

### Frontend (React)
```bash
cd ../frontend
npm install
npm start
```


