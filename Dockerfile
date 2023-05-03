FROM python:3.11.3-slim

# sudo
RUN apt-get update && \
    apt-get install -y sudo && \
    rm -rf /var/lib/apt/lists/* && \
    echo "appuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Set up a app user
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser

# Install system and build dependencies for gmpy2
RUN sudo apt-get update && \
    sudo apt-get install -y libgmp-dev libmpfr-dev libmpc-dev gcc && \
    sudo rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the required code
COPY --chown=appuser:appuser . .

# Expose port from the environment variable
EXPOSE ${PORT}

# create mysql tables and starup application
CMD python -m alembic upgrade head && python -m gunicorn -k uvicorn.workers.UvicornWorker -w ${WEB_CONCURRENCY} -b 0.0.0.0:${PORT} src.main:app ${GUNICORN_CMD_ARGS}