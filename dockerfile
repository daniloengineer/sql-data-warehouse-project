FROM apache/airflow:3.2.1

USER root

# Install system dependencies for MSSQL ODBC Driver (Debian 12 / Bookworm)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev \
    && apt-get autoremove -yqq --purge \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install the Airflow MSSQL provider 
# It's good practice to pre-install these for your ETL work
RUN pip install --no-cache-dir \
    apache-airflow-providers-microsoft-mssql \
    pymssql