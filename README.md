# CanteenX – Smart Campus Food Ordering & Canteen Management System
### Medi-Caps University, Indore, Madhya Pradesh, India

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=flat&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-18.x-61DAFB?style=flat&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Production-336791?style=flat&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

A centralized campus food ordering platform connecting students with university canteens. Students can browse menus, add items to cart, place orders, and track them in real time — while canteen staff manage everything from a dedicated admin dashboard.

---

## ✨ Features

### 🎓 Student Portal
- 🔐 Secure registration & authentication (JWT)
- 🍔 Browse food menu with search & filters
- 🛒 Real-time shopping cart
- 📦 Order placement & tracking
- 🔔 Order status notifications
- 📊 Order history

### 🏪 Canteen Admin Portal
- 📈 Real-time dashboard with analytics
- 🍽️ Food & category management
- 📋 Order management & status updates
- 📊 Sales reports & revenue analytics
- 🔔 New order notifications

### 🛡️ Super Admin Panel
- 👥 User management
- 🏪 Canteen management
- 📊 System-wide analytics

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React.js | 18.x | UI Framework |
| Vite | 5.x | Build Tool |
| Tailwind CSS | 3.x | Styling |
| React Router DOM | 6.x | Navigation |
| Axios | 1.x | HTTP Client |
| Recharts | 2.x | Charts & Analytics |
| Lucide React | latest | Icons |
| React Hot Toast | latest | Notifications |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Language |
| Django | 4.2+ | Web Framework |
| Django REST Framework | 3.14+ | REST API |
| SimpleJWT | 5.x | JWT Authentication |
| django-cors-headers | 4.x | CORS Handling |
| Pillow | 10.x | Image Processing |
| python-decouple | 3.x | Environment Config |

### Database
- **SQLite** — Default for development (zero config)
- **PostgreSQL** — Recommended for production

---

## 📁 Project Structure

```
canteenX/
├── backend/                   # Django project root
│   ├── config/                # Django settings package
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── accounts/              # User auth & profiles
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── canteens/              # Canteen management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── menu/                  # Food items & categories
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── cart/                  # Shopping cart
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── orders/                # Order placement & tracking
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── notifications/         # Order status notifications
│   │   ├── models.py
│   │   ├── views.py
│   │   └── migrations/
│   ├── analytics/             # Sales & revenue analytics
│   │   ├── views.py
│   │   └── urls.py
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                  # React + Vite app
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons.svg
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── venv/                      # Python virtual environment (not committed)
├── .env                       # Local environment variables (not committed)
├── .env.example               # Environment variable template
├── .gitignore
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm 9+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/canteenx.git
cd canteenx
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example env file to the **root** of the project:

```bash
# From the canteenX root folder
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-very-secret-key-here-change-this
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# For PostgreSQL (production):
# DATABASE_URL=postgresql://user:password@localhost:5432/canteenx

ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. Database Setup

```bash
cd backend

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Seed initial data: canteen, admin accounts, sample menu
python manage.py create_initial_data
```

### 5. Create Super Admin (optional — if not seeded)

```bash
python manage.py createsuperuser
```

**Default accounts created by `create_initial_data`:**

| Role | Email | Password |
|---|---|---|
| Super Admin | admin@medicaps.ac.in | Admin@123 |
| Canteen Admin | canteen@medicaps.ac.in | Canteen@123 |

> ⚠️ Change these credentials immediately in any non-development environment.

### 6. Start Backend Server

```bash
cd backend
python manage.py runserver
```

| URL | Description |
|---|---|
| http://localhost:8000 | Backend root |
| http://localhost:8000/api/ | API root |
| http://localhost:8000/admin/ | Django admin panel |

### 7. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

### 8. Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 🔗 API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Student registration |
| POST | `/api/auth/login/` | User login |
| POST | `/api/auth/logout/` | Logout (blacklist token) |
| POST | `/api/auth/token/refresh/` | Refresh access token |

### Student
| Method | Endpoint | Description |
|---|---|---|
| GET/PUT | `/api/student/profile/` | View / update profile |
| POST | `/api/student/change-password/` | Change password |

### Menu (Public)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/canteens/` | List canteens |
| GET | `/api/food/categories/` | List categories |
| GET | `/api/food/items/` | List food items |
| GET | `/api/food/items/{id}/` | Food item detail |

### Cart
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/cart/` | View cart |
| POST | `/api/cart/add/` | Add item to cart |
| PUT | `/api/cart/update/` | Update item quantity |
| DELETE | `/api/cart/remove/` | Remove item |
| DELETE | `/api/cart/clear/` | Clear entire cart |

### Orders
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/orders/` | Place order |
| GET | `/api/orders/` | Student order history |
| GET | `/api/orders/{id}/` | Order detail |

### Admin (Canteen Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/dashboard/` | Dashboard stats |
| GET | `/api/admin/analytics/` | Sales analytics |
| GET | `/api/admin/reports/` | Reports (filterable by date) |
| GET | `/api/admin/orders/` | All canteen orders |
| PATCH | `/api/admin/orders/{id}/status/` | Update order status |
| GET/POST | `/api/admin/food/items/` | List / create food items |
| GET/PUT/DELETE | `/api/admin/food/items/{id}/` | Manage food item |
| GET/POST | `/api/admin/food/categories/` | List / create categories |
| GET/PUT/DELETE | `/api/admin/food/categories/{id}/` | Manage category |

---

## 🔐 Security

- **JWT authentication** — access token: 60 min, refresh token: 7 days
- **Role-based access control** — Student / Canteen Admin / Super Admin
- **Secure password hashing** — Django's PBKDF2 with SHA-256
- **CORS** — configured for frontend origin only
- **Per-request permission checks** — backend validates every request
- **Token blacklisting** — logout invalidates refresh tokens
- Sensitive endpoints require authentication; plain-text passwords are never stored

---

## 👤 User Roles

| Role | Access |
|---|---|
| **Student** | Browse menu, manage cart, place & track orders, view profile |
| **Canteen Admin** | Manage own canteen's food items, categories, orders, and analytics |
| **Super Admin** | Full access — all users, all canteens, system-wide statistics, Django admin |

---

## 🗄️ PostgreSQL Setup (Production)

```bash
# Install PostgreSQL, then run:
psql -U postgres
```

```sql
CREATE DATABASE canteenx;
CREATE USER canteenx_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE canteenx TO canteenx_user;
\q
```

```bash
# Install psycopg2 driver
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://canteenx_user:secure_password@localhost:5432/canteenx

# Apply migrations
python manage.py migrate
```

---

## 📱 Screenshots

> _Student Dashboard · Menu Browser · Shopping Cart · Order Tracking · Admin Dashboard · Order Management_
>
> _(Screenshots will be added once the UI is finalized.)_

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add: your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🏫 About

**CanteenX** was built as a capstone project for **Medi-Caps University**, Indore, Madhya Pradesh, India — aiming to digitize and streamline the campus canteen experience for students and staff alike.
