FROM gradle:8.5-jdk17 AS builder
WORKDIR /app
COPY . .
RUN gradle :auth-service:build --no-daemon

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/build/libs/auth-service-1.0.0.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar"]
