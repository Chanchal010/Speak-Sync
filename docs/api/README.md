# Speak-Sync API Documentation

This directory contains the API documentation and Postman collections for the Speak-Sync project.

## 📁 Files

- **`Speak-Sync-API.postman_collection.json`** - Complete Postman collection with all API endpoints
- **`Speak-Sync-Development.postman_environment.json`** - Development environment configuration

## 🚀 Quick Start

### Import into Postman

1. Open Postman
2. Click **Import** button (top left)
3. Import both files:
   - `Speak-Sync-API.postman_collection.json`
   - `Speak-Sync-Development.postman_environment.json`
4. Select the **Speak-Sync Development** environment from the dropdown (top right)
5. Start making requests!

## 🔐 Authentication Flow

The collection includes automatic token management. Here's the recommended flow:

1. **Register** or **Login** → Tokens are automatically saved to environment variables
2. **Use Protected Endpoints** → Access token is automatically included in headers
3. **Refresh Token** → When access token expires, use refresh endpoint to get new tokens
4. **Logout** → Invalidates the current access token

## 📋 Available Endpoints

### Health Check
- `GET /health` - Check if Gateway Service is running

### Authentication (`/api/auth`)

#### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user account |
| POST | `/api/auth/login` | Login with email and password |
| POST | `/api/auth/refresh` | Refresh access token using refresh token |

#### Protected Endpoints (Requires Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/logout` | Logout and invalidate access token |
| GET | `/api/auth/me` | Get current authenticated user info |

## 📝 Request Examples

### Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user-id",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user"
    },
    "tokens": {
      "accessToken": "eyJhbGc...",
      "refreshToken": "eyJhbGc..."
    }
  }
}
```

### Login User

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user-id",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user"
    },
    "tokens": {
      "accessToken": "eyJhbGc...",
      "refreshToken": "eyJhbGc..."
    }
  }
}
```

### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user-id",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "isActive": true,
      "createdAt": "2025-11-28T17:00:00.000Z"
    }
  }
}
```

### Refresh Token

```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refreshToken": "eyJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tokens": {
      "accessToken": "eyJhbGc...",
      "refreshToken": "eyJhbGc..."
    }
  }
}
```

### Logout

```http
POST /api/auth/logout
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

## 🔧 Environment Variables

The Postman environment includes these variables:

| Variable | Description | Auto-Updated |
|----------|-------------|--------------|
| `BASE_URL` | API base URL (default: `http://localhost:3000`) | No |
| `ACCESS_TOKEN` | JWT access token for authentication | Yes |
| `REFRESH_TOKEN` | JWT refresh token for token renewal | Yes |
| `USER_ID` | Current authenticated user ID | Yes |

Variables marked as "Auto-Updated" are automatically set by the collection's test scripts after successful authentication.

## ⚠️ Error Responses

All endpoints follow a consistent error response format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Validation error or malformed request
- `401 Unauthorized` - Authentication required or invalid credentials
- `409 Conflict` - Resource already exists (e.g., email already registered)
- `500 Internal Server Error` - Server error

## 🛠️ Development Setup

Before using the API, ensure the Gateway Service is running:

```bash
# From project root
cd apps/gateway-service
pnpm install
pnpm dev
```

The service will start on `http://localhost:3000` by default.

## 📚 Additional Resources

- [Project README](../../README.md)
- [Service Startup Guide](../../START_SERVICES.md)
- [Architecture Documentation](../architecture/)

## 🤝 Contributing

When adding new endpoints:

1. Update the Postman collection
2. Add examples to this README
3. Include test scripts for automatic token management
4. Document request/response formats

---

**Last Updated:** 2025-11-28
