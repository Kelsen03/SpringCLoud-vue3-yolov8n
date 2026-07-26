FROM maven:3.8.6-openjdk-8-slim AS builder
WORKDIR /build
COPY pom.xml ./
COPY supermarket-gateway/pom.xml ./supermarket-gateway/pom.xml
COPY supermarket-auth/pom.xml ./supermarket-auth/pom.xml
COPY supermarket-product/pom.xml ./supermarket-product/pom.xml
COPY supermarket-inventory/pom.xml ./supermarket-inventory/pom.xml
COPY supermarket-order/pom.xml ./supermarket-order/pom.xml
COPY supermarket-analysis/pom.xml ./supermarket-analysis/pom.xml
RUN mvn dependency:go-offline -B -q
COPY supermarket-gateway/src ./supermarket-gateway/src
COPY supermarket-auth/src ./supermarket-auth/src
COPY supermarket-product/src ./supermarket-product/src
COPY supermarket-inventory/src ./supermarket-inventory/src
COPY supermarket-order/src ./supermarket-order/src
COPY supermarket-analysis/src ./supermarket-analysis/src
RUN mvn clean package -DskipTests -B -q
FROM openjdk:8-jre-alpine
RUN apk add --no-cache tzdata curl && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
RUN addgroup -g 1000 app && adduser -u 1000 -G app -D appuser
WORKDIR /app
COPY --from=builder /build/supermarket-analysis/target/*.jar app.jar
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:9004/actuator/health || exit 1
USER appuser
ENTRYPOINT ["sh", "-c", "java -jar -XX:+UseG1GC -XX:MaxRAMPercentage=75.0 app.jar"]
