FROM gradle:8.5-jdk17 AS builder
WORKDIR /app
COPY . .
RUN gradle :post-service:build --no-daemon

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/build/libs/post-service-1.0.0.jar app.jar
EXPOSE 8083
ENTRYPOINT ["java", "-jar", "app.jar"]
