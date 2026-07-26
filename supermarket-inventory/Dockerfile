FROM eclipse-temurin:8-jre-alpine
RUN apk add --no-cache tzdata curl && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
RUN addgroup -g 1000 app && adduser -u 1000 -G app -D appuser
WORKDIR /app
COPY target/*.jar app.jar
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:9002/actuator/health || exit 1
USER appuser
ENTRYPOINT ["sh", "-c", "java -jar -XX:+UseG1GC -XX:MaxRAMPercentage=75.0 app.jar"]
