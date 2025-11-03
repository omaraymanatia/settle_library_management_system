# Library Management System API

A comprehensive RESTful API for managing a library system built with FastAPI, SQLAlchemy, and PostgreSQL. The system supports user authentication, book management, reservations, borrowing, and payment processing with role-based access control.

## 🏗️ Architecture

```
server/
├── app/
│   ├── api/              # API route handlers
│   ├── crud/             # Database CRUD operations
│   ├── db/               # Database configuration
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic services
│   ├── config.py         # Application configuration
│   └── main.py           # FastAPI application setup
├── start_server.py       # Server startup script
├── seed_database.py      # Database seeding script
├── check_database.py     # Database verification script
└── requirements.txt      # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database
- pip package manager

### Installation

1. **Clone the repository and navigate to server directory:**
   ```bash
   cd server
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the server directory:
   ```env
   DATABASE_URL=postgresql://username:password@localhost/library_db
   SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DEBUG=true
   ENVIRONMENT=development
   RESERVATION_EXPIRY_HOURS=24
   DEPOSIT_PERCENTAGE=0.1
   ```

4. **Seed the database with sample data:**
   ```bash
   python seed_database.py
   ```

5. **Start the server:**
   ```bash
   python start_server.py
   ```

The API will be available at `http://localhost:8000`

### Quick Commands

- **Check database contents:** `python check_database.py`
- **Seed database:** `python seed_database.py`
- **Start server:** `python start_server.py`

## 📱 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Interactive Documentation
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Sample Credentials (After Seeding)
- **Admin:** `admin@library.com` / `admin123`
- **Librarian:** `librarian@library.com` / `librarian123`
- **User:** `john@example.com` / `user123`

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **USER** | Browse books, create reservations, borrow books, view own data |
| **LIBRARIAN** | All user permissions + manage books, approve borrows, manage all reservations |
| **ADMIN** | All permissions + manage users, delete books, access all data |

## 📚 Core Entities

### Book Classes
Books are categorized into classes with different pricing:

| Class | Borrow Fee | Deposit | Fine/Day |
|-------|------------|---------|----------|
| **A** | $10.00 | $5.00 | $1.00 |
| **B** | $15.00 | $8.00 | $1.50 |
| **C** | $20.00 | $10.00 | $2.00 |

### Entity Relationships
```
User -> Reservations -> Books
User -> Borrows -> Books
User -> Payments
Reservations -> Payments (deposits)
Borrows -> Payments (fees/fines)
Books -> BookClass
```

## 🔗 API Endpoints

### Authentication Endpoints

#### POST `/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "created_at": "2024-01-01T12:00:00Z",
  "message": "User registered successfully"
}
```

#### POST `/auth/login`
Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

#### POST `/auth/logout`
Logout user (client-side token removal).
**Auth Required:** ✅

#### POST `/auth/refresh`
Refresh access token.
**Auth Required:** ✅

#### GET `/auth/verify`
Verify token validity.
**Auth Required:** ✅

### Book Management Endpoints

#### GET `/books/`
Get all books with pagination and filtering.

**Query Parameters:**
- `skip` (int): Number of books to skip (default: 0)
- `limit` (int): Number of books to return (default: 100, max: 1000)
- `search` (string): Search by title, author, or ISBN
- `book_class_id` (int): Filter by book class
- `available_only` (bool): Show only available books

**Response:**
```json
[
  {
    "id": 1,
    "isbn": "9780451524935",
    "title": "1984",
    "author": "George Orwell",
    "shelf_location": "Fiction-A1",
    "total_quantity": 5,
    "available_quantity": 4,
    "created_at": "2024-01-01T12:00:00Z",
    "book_class": {
      "id": 1,
      "name": "A",
      "borrow_fee": 10.0,
      "deposit_amount": 5.0,
      "fine_per_day": 1.0
    }
  }
]
```

#### POST `/books/`
Create a new book.
**Auth Required:** ✅ (Librarian/Admin)

**Request Body:**
```json
{
  "isbn": "9780451524935",
  "title": "1984",
  "author": "George Orwell",
  "shelf_location": "Fiction-A1",
  "total_quantity": 5,
  "available_quantity": 5,
  "book_class_id": 1
}
```

#### GET `/books/{book_id}`
Get a specific book by ID.

#### GET `/books/isbn/{isbn}`
Get a specific book by ISBN.

#### PATCH `/books/{book_id}`
Update a book.
**Auth Required:** ✅ (Librarian/Admin)

#### DELETE `/books/{book_id}`
Delete a book.
**Auth Required:** ✅ (Admin)

#### GET `/books/available`
Get all available books.

#### PATCH `/books/{book_id}/availability`
Update book availability quantity.
**Auth Required:** ✅ (Librarian/Admin)

### User Management Endpoints

#### GET `/users/me`
Get current user information.
**Auth Required:** ✅

#### GET `/users/`
Get all users (with pagination).
**Auth Required:** ✅ (Admin)

#### GET `/users/{user_id}`
Get specific user by ID.
**Auth Required:** ✅ (Admin or own profile)

#### PATCH `/users/me`
Update current user profile.
**Auth Required:** ✅

#### PATCH `/users/{user_id}`
Update any user.
**Auth Required:** ✅ (Admin)

#### DELETE `/users/{user_id}`
Delete a user.
**Auth Required:** ✅ (Admin)

### Reservation Endpoints

#### POST `/reservations/`
Create a new book reservation.
**Auth Required:** ✅

**Request Body:**
```json
{
  "book_id": 1,
  "deposit_amount": 5.0
}
```

**Response:**
```json
{
  "reservation": {
    "id": 1,
    "book_id": 1,
    "user_id": 1,
    "status": "pending",
    "expiry_date": "2024-01-02T12:00:00Z"
  },
  "payment_id": 1,
  "message": "Reservation created. Please complete the deposit payment to confirm."
}
```

#### PUT `/reservations/{reservation_id}/confirm-payment`
Confirm reservation payment.
**Auth Required:** ✅

#### GET `/reservations/my-reservations`
Get current user's reservations.
**Auth Required:** ✅

#### GET `/reservations/`
Get all reservations.
**Auth Required:** ✅ (Librarian/Admin)

#### PATCH `/reservations/{reservation_id}`
Update reservation status.
**Auth Required:** ✅ (Librarian/Admin)

#### DELETE `/reservations/{reservation_id}`
Cancel a reservation.
**Auth Required:** ✅

### Borrowing Endpoints

#### POST `/borrows/`
Create a borrow request.
**Auth Required:** ✅

**Request Body:**
```json
{
  "book_id": 1,
  "reservation_id": 1,
  "due_date": "2024-01-15T12:00:00Z"
}
```

#### GET `/borrows/my-borrows`
Get current user's borrows.
**Auth Required:** ✅

#### GET `/borrows/`
Get all borrows.
**Auth Required:** ✅ (Librarian/Admin)

#### GET `/borrows/{borrow_id}`
Get specific borrow details.
**Auth Required:** ✅

#### PUT `/borrows/{borrow_id}/approve`
Approve or reject a borrow request.
**Auth Required:** ✅ (Librarian/Admin)

**Request Body:**
```json
{
  "approve": true
}
```

#### PUT `/borrows/{borrow_id}/return`
Return a borrowed book.
**Auth Required:** ✅ (Librarian/Admin)

#### GET `/borrows/overdue`
Get all overdue borrows.
**Auth Required:** ✅ (Librarian/Admin)

### Payment Endpoints

#### POST `/payments/`
Create a payment.
**Auth Required:** ✅

**Request Body:**
```json
{
  "amount": 10.0,
  "payment_type": "borrow_fee",
  "status": "paid",
  "user_id": 1
}
```

#### GET `/payments/my-payments`
Get current user's payments.
**Auth Required:** ✅

#### GET `/payments/`
Get all payments.
**Auth Required:** ✅ (Admin)

#### GET `/payments/{payment_id}`
Get specific payment details.
**Auth Required:** ✅

#### PATCH `/payments/{payment_id}`
Update payment status.
**Auth Required:** ✅ (Librarian/Admin)

## 📊 Database Schema

### Core Models

#### User
- `id`: Primary key
- `name`: User's full name
- `email`: Unique email address
- `password`: Hashed password
- `role`: User role (user/librarian/admin)
- `created_at`: Account creation timestamp

#### BookClass
- `id`: Primary key
- `name`: Class name (A/B/C)
- `borrow_fee`: Fee for borrowing
- `deposit_amount`: Required deposit
- `fine_per_day`: Daily fine for overdue books

#### Book
- `id`: Primary key
- `isbn`: Unique ISBN
- `title`: Book title
- `author`: Book author
- `shelf_location`: Physical location
- `total_quantity`: Total copies
- `available_quantity`: Available copies
- `book_class_id`: Foreign key to BookClass

#### Reservation
- `id`: Primary key
- `user_id`: Foreign key to User
- `book_id`: Foreign key to Book
- `payment_id`: Foreign key to Payment
- `reservation_date`: When reserved
- `expiry_date`: When reservation expires
- `status`: Reservation status

#### Borrow
- `id`: Primary key
- `user_id`: Foreign key to User
- `book_id`: Foreign key to Book
- `reservation_id`: Optional foreign key to Reservation
- `payment_id`: Foreign key to Payment
- `borrow_date`: When borrowed
- `due_date`: When due back
- `return_date`: When returned (if applicable)
- `status`: Borrow status

#### Payment
- `id`: Primary key
- `user_id`: Foreign key to User
- `amount`: Payment amount
- `payment_type`: Type (deposit/borrow_fee/fine)
- `status`: Payment status
- `payment_date`: When payment was made

## 🔄 Business Logic

### Reservation Flow
1. User creates reservation → `PENDING` status
2. Deposit payment created → `PENDING` status
3. User confirms payment → Reservation becomes `RESERVED`
4. Reservation expires after 24 hours if not used

### Borrowing Flow
1. User creates borrow request → `PENDING_APPROVAL` status
2. Librarian approves/rejects → `BORROWED` or `REJECTED`
3. Borrow fee payment processed
4. Book availability decremented
5. Due date calculated based on book class

### Return Flow
1. Librarian processes return → `RETURNED` status
2. Book availability incremented
3. Late fees calculated if overdue
4. Deposit refunded if applicable

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: BCrypt for secure password storage
- **Role-Based Access Control**: Fine-grained permissions
- **Input Validation**: Pydantic schema validation
- **CORS Protection**: Configured for allowed origins
- **SQL Injection Protection**: SQLAlchemy ORM

## 📝 Status Enums

### Reservation Status
- `PENDING`: Awaiting payment confirmation
- `RESERVED`: Active reservation
- `BORROWED`: Book has been borrowed
- `EXPIRED`: Reservation has expired

### Borrow Status
- `PENDING_APPROVAL`: Awaiting librarian approval
- `REJECTED`: Request rejected by librarian
- `BORROWED`: Currently borrowed
- `RETURN_PENDING`: Return requested
- `RETURNED`: Successfully returned
- `LATE`: Overdue return

### Payment Status
- `PENDING`: Payment not yet processed
- `PAID`: Payment completed successfully
- `FAILED`: Payment failed

### Payment Types
- `DEPOSIT`: Reservation deposit
- `BORROW_FEE`: Book borrowing fee
- `FINE`: Overdue fine

## 🧪 Testing

### Manual Testing
1. **Start the server:** `python start_server.py`
2. **Visit Swagger UI:** `http://localhost:8000/docs`
3. **Test endpoints** using the interactive documentation

### Database Testing
- **Check data:** `python check_database.py`
- **Reset and seed:** `python seed_database.py`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing secret | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |
| `DEBUG` | Debug mode | `False` |
| `ENVIRONMENT` | Environment name | `development` |
| `RESERVATION_EXPIRY_HOURS` | Reservation expiry | `24` |
| `DEPOSIT_PERCENTAGE` | Deposit percentage | `0.1` |

### CORS Configuration
The API allows requests from:
- `http://localhost:3000` (React development)
- `http://localhost:5500` (Live Server)
- `http://localhost:8080` (Alternative development)

## 🚨 Error Handling

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Internal Server Error

### Error Response Format
```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "status_code": 400
}
```

## 📦 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings
- **PostgreSQL**: Database (psycopg2-binary)
- **Uvicorn**: ASGI server
- **Python-JOSE**: JWT token handling
- **Passlib**: Password hashing
- **Python-dotenv**: Environment variable management

### Development Dependencies
- **Alembic**: Database migrations

## 🔄 Database Migrations

While the current setup uses `Base.metadata.create_all()` for simplicity, Alembic is included for future migration needs:

```bash
# Initialize migrations (when needed)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🎯 Future Enhancements

### Planned Features
- [ ] Email notifications for overdue books
- [ ] Advanced search and filtering
- [ ] Book recommendations
- [ ] Reading history and analytics
- [ ] Multi-branch library support
- [ ] Mobile app integration API
- [ ] Automated fine calculations
- [ ] Book review and rating system

### Technical Improvements
- [ ] Redis caching for frequently accessed data
- [ ] Background task processing with Celery
- [ ] API rate limiting
- [ ] Comprehensive test suite
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Monitoring and logging
- [ ] API versioning strategy

## 📞 Support

For issues, questions, or contributions:
1. Check the interactive API documentation at `/docs`
2. Review the database seeding and checking scripts
3. Examine the source code for detailed implementation
4. Test endpoints using the provided sample data

---

**Built with ❤️ using FastAPI, SQLAlchemy, and PostgreSQL**