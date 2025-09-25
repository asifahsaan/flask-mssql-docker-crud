FROM python:3.11-slim-bullseye
ARG DEBIAN_FRONTEND=noninteractive

# Force HTTPS mirrors and disable proxies to avoid ISP interception
RUN printf 'Acquire::http::Proxy "false";\nAcquire::https::Proxy "false";\n' > /etc/apt/apt.conf.d/99no-proxy \
 && sed -i 's|http://deb.debian.org|https://deb.debian.org|g; s|http://security.debian.org|https://security.debian.org|g' /etc/apt/sources.list

# System deps (ODBC + toolchain + CA certs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg2 ca-certificates unixodbc unixodbc-dev gcc g++ \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Microsoft ODBC Driver 18 for SQL Server (Debian 11 repo works best with bullseye base)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
      | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" \
      > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
 && rm -rf /var/lib/apt/lists/*

# App
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Default envs (override at run time if you want)
ENV ODBC_DRIVER="ODBC Driver 18 for SQL Server"
ENV DB_SERVER="host.docker.internal"
ENV DB_PORT="1433"
ENV DB_NAME="test"
ENV DB_USER="flask_user"
ENV DB_PASSWORD="123"

EXPOSE 5000
CMD ["python", "app.py"]
