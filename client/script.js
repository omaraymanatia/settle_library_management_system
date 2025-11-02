// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
let currentUser = null;
let currentPage = 1;
const itemsPerPage = 12;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    loadBooks();
});

// Debug Functions
function debugAuth() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');

    console.log('🔍 Auth Debug Info:');
    console.log('Token exists:', !!token);
    console.log('Token:', token ? token.substring(0, 50) + '...' : 'null');
    console.log('User:', user ? JSON.parse(user) : 'null');

    if (token) {
        try {
            // Decode JWT payload (without verification)
            const payload = JSON.parse(atob(token.split('.')[1]));
            console.log('Token payload:', payload);
            console.log('Token expires:', new Date(payload.exp * 1000));
            console.log('Token expired:', Date.now() > payload.exp * 1000);
        } catch (e) {
            console.log('Error decoding token:', e);
        }
    }
}

// Add to window for console access
window.debugAuth = debugAuth;

// Authentication Management
function checkAuthStatus() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');

    if (token && user) {
        currentUser = JSON.parse(user);
        updateUIForLoggedInUser();
    } else {
        updateUIForLoggedOutUser();
    }
}

function updateUIForLoggedInUser() {
    document.getElementById('auth-link').style.display = 'none';
    document.getElementById('dashboard-link').style.display = 'inline';
    document.getElementById('logout-btn').style.display = 'inline';
}

function updateUIForLoggedOutUser() {
    document.getElementById('auth-link').style.display = 'inline';
    document.getElementById('dashboard-link').style.display = 'none';
    document.getElementById('logout-btn').style.display = 'none';
    currentUser = null;
}

// Navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Show target section
    document.getElementById(sectionId).classList.add('active');

    // Load section-specific data
    if (sectionId === 'dashboard' && currentUser) {
        loadDashboardData();
    }
}

function showTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');

    // Load tab-specific data
    if (tabId === 'my-borrows') {
        loadUserBorrows();
    } else if (tabId === 'my-reservations') {
        loadUserReservations();
    } else if (tabId === 'my-payments') {
        loadUserPayments();
    }
}

// Authentication Functions
async function login(event) {
    event.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    // Validate password length (bcrypt limitation)
    if (new Blob([password]).size > 72) {
        showToast('Password is too long (maximum 72 bytes)', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            currentUser = data.user;

            updateUIForLoggedInUser();
            showToast('Login successful!', 'success');
            showSection('books');

            // Reload books to show updated UI with login status
            loadBooks(currentPage);

            // Clear form
            document.getElementById('login-email').value = '';
            document.getElementById('login-password').value = '';
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function register(event) {
    event.preventDefault();

    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    // Validate password length (bcrypt limitation)
    if (new Blob([password]).size > 72) {
        showToast('Password is too long (maximum 72 bytes)', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Registration successful! Please login.', 'success');
            toggleAuthForm();

            // Clear form
            document.getElementById('register-name').value = '';
            document.getElementById('register-email').value = '';
            document.getElementById('register-password').value = '';
        } else {
            showToast(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Registration failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    currentUser = null;
    updateUIForLoggedOutUser();
    showToast('Logged out successfully', 'success');
    showSection('books');

    // Reload books to show updated UI without login status
    loadBooks(currentPage);
}

function toggleAuthForm() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    loginForm.classList.toggle('active');
    registerForm.classList.toggle('active');
}

// Books Functions
async function loadBooks(page = 1) {
    showLoading(true);
    currentPage = page;

    try {
        const searchTerm = document.getElementById('search-input').value;
        const availableOnly = document.getElementById('available-only').checked;

        let url = `${API_BASE_URL}/books/?skip=${(page - 1) * itemsPerPage}&limit=${itemsPerPage}`;

        if (searchTerm) {
            url += `&search=${encodeURIComponent(searchTerm)}`;
        }

        if (availableOnly) {
            url += '&available_only=true';
        }

        const response = await fetch(url);
        const books = await response.json();

        if (response.ok) {
            displayBooks(books);
            updatePagination(books.length);
        } else {
            showToast('Failed to load books', 'error');
        }
    } catch (error) {
        console.error('Error loading books:', error);
        showToast('Failed to load books', 'error');
    } finally {
        showLoading(false);
    }
}

function displayBooks(books) {
    const booksGrid = document.getElementById('books-grid');

    if (books.length === 0) {
        booksGrid.innerHTML = '<div class="no-results">No books found</div>';
        return;
    }

    booksGrid.innerHTML = books.map(book => `
        <div class="book-card" onclick="showBookDetails(${book.id})">
            <h3>${book.title}</h3>
            <p class="author">by ${book.author}</p>
            <p class="isbn">ISBN: ${book.isbn}</p>
            <div class="availability">
                <span class="availability-badge ${book.available_quantity > 0 ? 'available' : 'unavailable'}">
                    ${book.available_quantity > 0 ? `${book.available_quantity} available` : 'Not available'}
                </span>
                <span class="total">Total: ${book.total_quantity}</span>
            </div>
            ${currentUser && book.available_quantity > 0 ? `
                <div class="book-actions">
                    <button class="btn btn-primary" onclick="event.stopPropagation(); borrowBook(${book.id})">
                        Borrow
                    </button>
                    <button class="btn btn-secondary" onclick="event.stopPropagation(); reserveBook(${book.id})">
                        Reserve
                    </button>
                </div>
            ` : !currentUser ? `
                <div class="book-actions">
                    <button class="btn btn-secondary" onclick="event.stopPropagation(); showSection('auth')">
                        Login to Borrow
                    </button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

function searchBooks() {
    loadBooks(1);
}

async function showBookDetails(bookId) {
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/books/${bookId}`);
        const book = await response.json();

        if (response.ok) {
            document.getElementById('book-details').innerHTML = `
                <h2>${book.title}</h2>
                <p><strong>Author:</strong> ${book.author}</p>
                <p><strong>ISBN:</strong> ${book.isbn}</p>
                <p><strong>Location:</strong> ${book.shelf_location || 'Not specified'}</p>
                <p><strong>Available:</strong> ${book.available_quantity} of ${book.total_quantity}</p>

                ${currentUser && book.available_quantity > 0 ? `
                    <div class="book-actions" style="margin-top: 1rem;">
                        <button class="btn btn-primary" onclick="borrowBook(${book.id}); closeModal();">
                            Borrow This Book
                        </button>
                        <button class="btn btn-secondary" onclick="reserveBook(${book.id}); closeModal();">
                            Reserve This Book
                        </button>
                    </div>
                ` : !currentUser ? `
                    <div class="book-actions" style="margin-top: 1rem;">
                        <button class="btn btn-secondary" onclick="showSection('auth'); closeModal();">
                            Login to Borrow
                        </button>
                    </div>
                ` : `
                    <p style="color: #e74c3c; margin-top: 1rem;">This book is currently not available</p>
                `}
            `;

            document.getElementById('book-modal').style.display = 'block';
        } else {
            showToast('Failed to load book details', 'error');
        }
    } catch (error) {
        console.error('Error loading book details:', error);
        showToast('Failed to load book details', 'error');
    } finally {
        showLoading(false);
    }
}

function closeModal() {
    document.getElementById('book-modal').style.display = 'none';
}

// Borrow and Reserve Functions
async function borrowBook(bookId) {
    if (!currentUser) {
        showToast('Please login to borrow books', 'warning');
        showSection('auth');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/borrows/request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ book_id: bookId })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Borrow request submitted successfully!', 'success');
            loadBooks(currentPage);
        } else {
            showToast(data.detail || 'Failed to submit borrow request', 'error');
        }
    } catch (error) {
        console.error('Error borrowing book:', error);
        showToast('Failed to submit borrow request', 'error');
    } finally {
        showLoading(false);
    }
}

async function reserveBook(bookId) {
    if (!currentUser) {
        showToast('Please login to reserve books', 'warning');
        showSection('auth');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/reservations/?book_id=${bookId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Reservation created successfully!', 'success');
            loadBooks(currentPage);
        } else {
            showToast(data.detail || 'Failed to create reservation', 'error');
        }
    } catch (error) {
        console.error('Error reserving book:', error);
        showToast('Failed to create reservation', 'error');
    } finally {
        showLoading(false);
    }
}

// Dashboard Functions
function loadDashboardData() {
    loadUserBorrows();
}

async function loadUserBorrows() {
    if (!currentUser) return;

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/borrows/my-borrows`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        const borrows = await response.json();

        if (response.ok) {
            displayUserBorrows(borrows);
        } else {
            showToast('Failed to load your borrows', 'error');
        }
    } catch (error) {
        console.error('Error loading borrows:', error);
        showToast('Failed to load your borrows', 'error');
    } finally {
        showLoading(false);
    }
}

function displayUserBorrows(borrows) {
    const borrowsList = document.getElementById('borrows-list');

    if (borrows.length === 0) {
        borrowsList.innerHTML = '<div class="no-results">No borrowed books found</div>';
        return;
    }

    borrowsList.innerHTML = borrows.map(borrow => `
        <div class="item-card">
            <h4>${borrow.book?.title || 'Book Title'}</h4>
            <p class="meta">
                Borrowed: ${new Date(borrow.borrow_date).toLocaleDateString()} |
                Due: ${new Date(borrow.due_date).toLocaleDateString()}
            </p>
            <span class="status-badge ${borrow.status.toLowerCase()}">
                ${borrow.status.replace('_', ' ')}
            </span>
            ${borrow.status === 'BORROWED' ? `
                <div class="book-actions" style="margin-top: 1rem;">
                    <button class="btn btn-primary" onclick="requestReturn(${borrow.id})">
                        Request Return
                    </button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function loadUserReservations() {
    if (!currentUser) return;

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/reservations/my-reservations`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        const reservations = await response.json();

        if (response.ok) {
            displayUserReservations(reservations);
        } else {
            showToast('Failed to load your reservations', 'error');
        }
    } catch (error) {
        console.error('Error loading reservations:', error);
        showToast('Failed to load your reservations', 'error');
    } finally {
        showLoading(false);
    }
}

function displayUserReservations(reservations) {
    const reservationsList = document.getElementById('reservations-list');

    if (reservations.length === 0) {
        reservationsList.innerHTML = '<div class="no-results">No reservations found</div>';
        return;
    }

    reservationsList.innerHTML = reservations.map(reservation => `
        <div class="item-card">
            <h4>${reservation.book?.title || 'Book Title'}</h4>
            <p class="meta">
                Reserved: ${new Date(reservation.reservation_date).toLocaleDateString()} |
                Expires: ${new Date(reservation.expiry_date).toLocaleDateString()}
            </p>
            <span class="status-badge ${reservation.status.toLowerCase()}">
                ${reservation.status.replace('_', ' ')}
            </span>
            ${reservation.status === 'PENDING' || reservation.status === 'RESERVED' ? `
                <div class="book-actions" style="margin-top: 1rem;">
                    <button class="btn btn-secondary" onclick="cancelReservation(${reservation.id})">
                        Cancel Reservation
                    </button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function loadUserPayments() {
    if (!currentUser) return;

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/payments/my-payments`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        const payments = await response.json();

        if (response.ok) {
            displayUserPayments(payments);
        } else {
            showToast('Failed to load your payments', 'error');
        }
    } catch (error) {
        console.error('Error loading payments:', error);
        showToast('Failed to load your payments', 'error');
    } finally {
        showLoading(false);
    }
}

function displayUserPayments(payments) {
    const paymentsList = document.getElementById('payments-list');

    if (payments.length === 0) {
        paymentsList.innerHTML = '<div class="no-results">No payments found</div>';
        return;
    }

    paymentsList.innerHTML = payments.map(payment => `
        <div class="item-card">
            <h4>${payment.payment_type.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}</h4>
            <p class="meta">
                Amount: $${payment.amount.toFixed(2)} |
                Date: ${new Date(payment.payment_date).toLocaleDateString()}
            </p>
            <span class="status-badge ${payment.status.toLowerCase()}">
                ${payment.status}
            </span>
        </div>
    `).join('');
}

// Action Functions
async function requestReturn(borrowId) {
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/borrows/${borrowId}/request-return`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Return request submitted successfully!', 'success');
            loadUserBorrows();
        } else {
            showToast(data.detail || 'Failed to submit return request', 'error');
        }
    } catch (error) {
        console.error('Error requesting return:', error);
        showToast('Failed to submit return request', 'error');
    } finally {
        showLoading(false);
    }
}

async function cancelReservation(reservationId) {
    if (!confirm('Are you sure you want to cancel this reservation?')) {
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/reservations/${reservationId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            showToast('Reservation cancelled successfully!', 'success');
            loadUserReservations();
        } else {
            const data = await response.json();
            showToast(data.detail || 'Failed to cancel reservation', 'error');
        }
    } catch (error) {
        console.error('Error cancelling reservation:', error);
        showToast('Failed to cancel reservation', 'error');
    } finally {
        showLoading(false);
    }
}

// Utility Functions
function updatePagination(itemCount) {
    const pagination = document.getElementById('pagination');
    const hasNextPage = itemCount === itemsPerPage;
    const hasPrevPage = currentPage > 1;

    pagination.innerHTML = `
        <button onclick="loadBooks(${currentPage - 1})" ${!hasPrevPage ? 'disabled' : ''}>
            Previous
        </button>
        <span>Page ${currentPage}</span>
        <button onclick="loadBooks(${currentPage + 1})" ${!hasNextPage ? 'disabled' : ''}>
            Next
        </button>
    `;
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.add('show');
    } else {
        loading.classList.remove('show');
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Event listeners
document.addEventListener('click', function(event) {
    if (event.target === document.getElementById('book-modal')) {
        closeModal();
    }
});

// Handle enter key in search
document.getElementById('search-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        searchBooks();
    }
});