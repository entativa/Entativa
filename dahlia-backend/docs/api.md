# Dahlia API Documentation

## Authentication
All endpoints require Bearer token except /auth/* endpoints.

```
Authorization: Bearer <access_token>
```

## Endpoints

### Auth
- POST /auth/login
- POST /auth/signup
- POST /auth/refresh
- POST /auth/logout

### Users
- GET /users/{id}
- PUT /users/{id}
- POST /users/{id}/follow
- DELETE /users/{id}/follow

### Posts
- POST /posts
- GET /posts/{id}
- DELETE /posts/{id}
- POST /posts/{id}/like
- DELETE /posts/{id}/like

### Feed
- GET /feed
- GET /feed/foryou
