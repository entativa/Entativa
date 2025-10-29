FROM gradle:8.5-jdk17 AS builder
WORKDIR /app
COPY . .
RUN gradle :notification-service:build --no-daemon

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/build/libs/notification-service-1.0.0.jar app.jar
EXPOSE 8085
ENTRYPOINT ["java", "-jar", "app.jar"]
