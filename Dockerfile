# Build stage for frontend
FROM node:16-alpine as frontend-build
WORKDIR /app/frontend
# Copy frontend files
COPY frontend/index.html .
COPY frontend/vercel.json .

# Final stage
FROM python:3.11-slim

# Install nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data/idx /app/data/processed /app/data/raw_pdfs

# Copy backend code
COPY backend/ ./backend/

# Copy frontend from build stage
COPY --from=frontend-build /app/frontend/index.html /usr/share/nginx/html/
COPY --from=frontend-build /app/frontend/vercel.json /usr/share/nginx/html/

# Create nginx configuration
RUN echo '\
server {\n\
    listen 80;\n\
    server_name localhost;\n\
    \n\
    location / {\n\
        root /usr/share/nginx/html;\n\
        index index.html;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    location /api/ {\n\
        proxy_pass http://127.0.0.1:8000/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
}\n'\
> /etc/nginx/conf.d/default.conf

# Create startup script (use /bin/sh for slimmer base images)
RUN echo '\
#!/bin/sh\n\
service nginx start\n\
cd /app/backend\n\
exec python run.py\n'\
> /app/start.sh && \
chmod +x /app/start.sh

# Expose port
EXPOSE 80

# Set environment variables
ENV PYTHONPATH=/app
ENV TRANSFORMERS_CACHE=/app/.cache/transformers

# Start the application using sh to avoid missing /bin/bash on slim images
CMD ["sh", "/app/start.sh"]