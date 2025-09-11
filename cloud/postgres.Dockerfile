# PostgreSQL container for Cloud Run
FROM postgres:15-alpine

# Set environment variables for PostgreSQL
ENV POSTGRES_DB=finreview
ENV POSTGRES_USER=finreview_user
ENV POSTGRES_PASSWORD=FlhugG77XDC1_0SlYUfhuzd-TkEySuwTtYFcV3luIh0

# Create data directory
RUN mkdir -p /var/lib/postgresql/data

# Copy initialization scripts (optional)
# COPY init.sql /docker-entrypoint-initdb.d/

# Expose PostgreSQL port
EXPOSE 5432

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pg_isready -U finreview_user -d finreview || exit 1

# Start PostgreSQL
CMD ["postgres"]
