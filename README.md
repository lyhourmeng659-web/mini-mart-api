# 🛒 Mini Mart E-Commerce REST API

A production-ready RESTful API for a mini mart e-commerce system built with Flask, SQLAlchemy, and JWT authentication.

---

## 🏗️ Architecture

```
mini-mart-api/
├── app/
│   ├── controllers/
│   │   ├── front/          # Customer-facing endpoints
│   │   │   ├── auth_controller.py
│   │   │   ├── product_controller.py
│   │   │   ├── cart_controller.py
│   │   │   └── order_controller.py
│   │   └── admin/          # Admin-only endpoints
│   │       ├── auth_controller.py
│   │       ├── user_controller.py
│   │       ├── category_controller.py
│   │       ├── product_controller.py
│   │       ├── order_controller.py
│   │       └── report_controller.py
│   ├── services/           # Business logic layer
│   ├── repositories/       # Database access layer
│   ├── models/             # SQLAlchemy ORM models
│   ├── middleware/         # JWT auth decorators
│   └── utils/              # Helpers (response, pagination, validators, file handler)
├── config/                 # Environment-based configuration
├── migrations/             # Flask-Migrate database migrations
├── tests/                  # Unit & integration tests
├── uploads/products/       # Uploaded product images
├── run.py                  # App entry point
├── seed.py                 # Database seeder
├── gunicorn.conf.py        # Production Gunicorn config
└── Mini_Mart_API.postman_collection.json
```

---

## ⚡ Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/lyhourmeng659-web/mini-mart-api.git
cd mini-mart-api

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Seed the Database

```bash
python seed.py
```

Output:
```
✅  Seed complete!
   Admin  → admin@minimart.com   / Admin@1234
   Alice  → alice@example.com    / Alice@1234
   Bob    → bob@example.com      / Bob@12345
   Categories: 8 | Products: 27 | Users: 3
```

### 4. Run Development Server

```bash
python run.py
# → http://localhost:5000
```

---

## 🗄️ Database Schema

```
roles          users          categories     products
─────────      ────────────   ──────────     ────────────
id             id             id             id
name           name           name           name
               email          description    description
               password_hash  is_active      price
               phone          created_at     stock
               address        updated_at     image
               role_id ──────────────────►  category_id ──► categories.id
               is_active                     is_active
               created_at                    created_at

cart                          orders                  order_items
────────────                  ──────────────────      ─────────────────
id                            id                      id
user_id ──► users.id          order_number            order_id ──► orders.id
product_id ──► products.id    user_id ──► users.id    product_id ──► products.id
quantity                      total_amount            quantity
created_at                    status                  unit_price
                              shipping_address        subtotal
                              notes
                              created_at
```

---

## 🔌 API Endpoints

### Base URL: `http://localhost:5000`

### 🌐 Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/front/categories` | List active categories |
| GET | `/api/front/products` | List products (paginated, filterable) |
| GET | `/api/front/products/:id` | Get product detail |

### 🔐 Customer Auth (`/api/front/auth`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register` | — | Register new account |
| POST | `/login` | — | Login, receive JWT |
| POST | `/logout` | ✅ | Invalidate token |
| GET | `/me` | ✅ | Get profile |
| POST | `/reset-password` | ✅ | Change password |

### 🛒 Cart (`/api/front/cart`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `` | ✅ | View cart |
| POST | `/add` | ✅ | Add item |
| PUT | `/update` | ✅ | Update quantity |
| DELETE | `/remove/:product_id` | ✅ | Remove item |
| DELETE | `/clear` | ✅ | Clear cart |

### 📦 Orders — Customer (`/api/front/orders`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/checkout` | ✅ | Place order from cart |
| GET | `` | ✅ | List my orders |
| GET | `/:id` | ✅ | Order detail |

### 🔑 Admin Auth (`/api/admin/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Admin login |
| POST | `/logout` | Admin logout |

### 👥 Admin — Users (`/api/admin/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `` | List users (search, paginate) |
| GET | `/:id` | Get user |
| POST | `` | Create user |
| PUT | `/:id` | Update user |
| DELETE | `/:id` | Delete user |

### 📂 Admin — Categories (`/api/admin/categories`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `` | List categories |
| GET | `/:id` | Get category |
| POST | `` | Create category |
| PUT | `/:id` | Update category |
| DELETE | `/:id` | Delete category |

### 📦 Admin — Products (`/api/admin/products`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `` | List products |
| GET | `/:id` | Get product |
| POST | `` | Create product (multipart + image) |
| PUT | `/:id` | Update product (multipart + image) |
| DELETE | `/:id` | Delete product |

### 🧾 Admin — Orders (`/api/admin/orders`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `` | List all orders (filter by status) |
| GET | `/:id` | Order detail with items |
| PUT | `/:id/status` | Update order status |

### 📊 Admin — Reports (`/api/admin/reports`)

| Method | Endpoint | Query Params | Description |
|--------|----------|-------------|-------------|
| GET | `/sales` | `period`, `start_date`, `end_date` | Sales summary |
| GET | `/sales/daily` | — | Today's sales |
| GET | `/sales/weekly` | — | This week |
| GET | `/sales/monthly` | — | This month |
| GET | `/sales/by-product` | `period` | Revenue by product |
| GET | `/sales/by-category` | `period` | Revenue by category |

---

## 📋 Standard Response Format

```json
{
  "success": true,
  "message": "Description of result",
  "data": {}
}
```

### Paginated Response

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "items": ["..."],
    "pagination": {
      "total": 100,
      "page": 1,
      "per_page": 10,
      "pages": 10
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request / Validation Error |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient role) |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 500 | Internal Server Error |

---

## 🧪 Testing with Postman

1. Import `Mini_Mart_API.postman_collection.json`
2. Collection variables are pre-configured (`base_url`, `admin_token`, `customer_token`)
3. Run **Admin Login** → token auto-saved
4. Run **Customer Login** → token auto-saved
5. Test any endpoint — all auth headers are handled automatically

---

## 🚀 Production Deployment

### Option 1: Render (Free)

```bash
# In Render dashboard:
# Build command: pip install -r requirements.txt && python seed.py
# Start command: gunicorn -c gunicorn.conf.py run:app
# Set env vars: DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, FLASK_ENV=production
```

### Option 2: VPS / Linux Server

```bash
# Install dependencies
sudo apt update && sudo apt install python3-pip python3-venv nginx -y

# Setup project
cd /var/www && git clone <repo> mini-mart-api
cd mini-mart-api && python3 -m venv venv
source venv/bin/activate && pip install -r requirements.txt
cp .env.example .env && nano .env  # Configure production values
python seed.py

# Run with Gunicorn
gunicorn -c gunicorn.conf.py run:app

# Nginx config (/etc/nginx/sites-available/minimart)
server {
    listen 80;
    server_name your-domain.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /api/uploads/ {
        alias /var/www/mini-mart-api/uploads/products/;
    }
}
```

### Option 3: Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-c", "gunicorn.conf.py", "run:app"]
```

---

## 🔐 Security Checklist

- [x] Passwords hashed with bcrypt
- [x] JWT tokens with expiry (1h access, 30d refresh)
- [x] Token blacklist on logout
- [x] Role-based access control (admin / customer)
- [x] Input validation on all endpoints
- [x] File upload type & size restrictions
- [x] CORS configurable via environment
- [x] Environment-based secrets (never hardcoded)

---

## 🧑‍💻 GitHub Workflow

```bash
git init
git remote add origin https://github.com/your-username/mini-mart-api.git
git add .
git commit -m "feat: initial Mini Mart API"
git branch -M main
git push -u origin main

# Feature branches
git checkout -b feature/auth
git checkout -b feature/products
git checkout -b feature/orders
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Flask 3.0 |
| ORM | SQLAlchemy + Flask-Migrate |
| Auth | Flask-JWT-Extended |
| Password | Flask-Bcrypt |
| CORS | Flask-CORS |
| Database | SQLite (dev) / PostgreSQL or MySQL (prod) |
| Server | Gunicorn |
| Image Upload | Werkzeug + Pillow |