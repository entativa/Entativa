# Dahlia Architecture

## Services

### Kotlin Services
- **api-gateway** (8080): REST API gateway
- **auth-service** (8081): Dahlia ID authentication
- **user-service** (8082): User profiles and relationships
- **post-service** (8083): Post CRUD operations
- **feed-service** (8084): Timeline generation
- **notification-service** (8085): Push notifications

### Python Services
- **media-service** (9000): Image processing, compression
- **search-service** (9001): Elasticsearch integration
- **recommendation-service** (9002): ML-based recommendations

## Tech Stack
- **Kotlin**: Ktor + Exposed + gRPC
- **Python**: FastAPI + TensorFlow/PyTorch
- **Databases**: PostgreSQL, Redis, Elasticsearch
- **Storage**: MinIO (S3-compatible)
- **Message Queue**: RabbitMQ
