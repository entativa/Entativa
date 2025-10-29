FROM swift:5.9 as builder
WORKDIR /build
COPY Package.* ./
RUN swift package resolve
COPY . .
RUN swift build -c release

FROM swift:5.9-slim
WORKDIR /app
COPY --from=builder /build/.build/release/dm-service ./
EXPOSE 8080
ENTRYPOINT ["./dm-service"]
