# Use lightweight Python 3.11 Alpine image
FROM python:3.11-alpine

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy application script
COPY ticket_summary.py .

# Switch to non-root user
USER appuser

# Set entrypoint to ticket_summary CLI tool
ENTRYPOINT ["python", "ticket_summary.py"]

# Default argument displays help
CMD ["--help"]
