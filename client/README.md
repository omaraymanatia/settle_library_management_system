# Library Management System - Frontend

A simple, minimal frontend for the Library Management System built with HTML, CSS, and JavaScript.

## Features

### Public Features (No Authentication Required)
- 📚 **Browse Books**: View all available books in the library
- 🔍 **Search Books**: Search by title, author, or ISBN
- 🔧 **Filter Books**: Filter to show only available books
- 📖 **Book Details**: View detailed information about each book

### User Features (Authentication Required)
- 🔐 **User Registration**: Create a new account
- 🔑 **User Login**: Secure authentication
- 📋 **My Dashboard**: Personal dashboard with tabs for:
  - **My Borrows**: View borrowed books and request returns
  - **My Reservations**: View and manage reservations
  - **My Payments**: View payment history
- 📤 **Borrow Books**: Submit borrow requests for available books
- 📅 **Reserve Books**: Create reservations for books
- ↩️ **Return Books**: Request return of borrowed books
- ❌ **Cancel Reservations**: Cancel active reservations

## File Structure

```
client/
├── index.html      # Main HTML structure
├── styles.css      # CSS styling and responsive design
├── script.js       # JavaScript functionality and API calls
└── README.md       # This file
```

## Setup and Usage

1. **Start the Backend Server**
   ```bash
   cd server
   python start_server.py
   ```

2. **Serve the Frontend**
   You can serve the frontend in several ways:

   **Option 1: Simple HTTP Server (Python)**
   ```bash
   cd client
   python -m http.server 3000
   ```

   **Option 2: Live Server (VS Code Extension)**
   - Install the "Live Server" extension in VS Code
   - Right-click on `index.html` and select "Open with Live Server"

   **Option 3: Any Static File Server**
   - Use any static file server to serve the client directory

3. **Access the Application**
   - Open your browser and navigate to `http://localhost:3000`
   - The backend API should be running on `http://localhost:8000`

## Configuration

The API base URL is configured in `script.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

If your backend runs on a different port or host, update this configuration.

## User Interface

### Navigation
- **Books**: Browse all available books (accessible to everyone)
- **Login**: Authentication page with login/register forms
- **Dashboard**: Personal dashboard (only visible when logged in)
- **Logout**: Sign out of the application

### Responsive Design
The interface is fully responsive and works on:
- 💻 Desktop computers
- 📱 Mobile phones
- 📱 Tablets

### Key Features
- **Real-time Updates**: Actions like borrowing and reserving update the UI immediately
- **Toast Notifications**: Success/error messages for user feedback
- **Loading Indicators**: Visual feedback during API calls
- **Modal Windows**: Detailed book information in overlay
- **Search & Filter**: Easy book discovery
- **Pagination**: Efficient browsing of large book collections

## API Integration

The frontend integrates with the following backend endpoints:

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Books
- `GET /books` - Get books with search and filtering
- `GET /books/{id}` - Get book details

### Borrowing
- `POST /borrow/request` - Create borrow request
- `GET /borrow/my-borrows` - Get user's borrows
- `POST /borrow/{id}/request-return` - Request return

### Reservations
- `POST /reservations/` - Create reservation
- `GET /reservations/my-reservations` - Get user's reservations
- `DELETE /reservations/{id}` - Cancel reservation

### Payments
- `GET /payments/my-payments` - Get user's payment history

## User Experience

### For Anonymous Users
1. Browse and search books without registration
2. View book details and availability
3. Prompted to login when trying to borrow/reserve

### For Registered Users
1. All anonymous features plus:
2. Borrow available books
3. Reserve books for later borrowing
4. Manage personal library activities
5. Track payment history
6. Request returns when ready

## Browser Compatibility

Compatible with all modern browsers:
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

## Technologies Used

- **HTML5**: Semantic structure
- **CSS3**: Modern styling with flexbox and grid
- **JavaScript (ES6+)**: Async/await, fetch API, modern syntax
- **No Framework Dependencies**: Pure vanilla JavaScript for simplicity

## Future Enhancements

Potential improvements could include:
- 💳 Payment processing integration
- 📧 Email notifications
- 📊 Reading statistics
- 📝 Book reviews and ratings
- 🔄 Real-time updates with WebSocket