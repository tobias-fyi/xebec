# Pull base image
FROM python:3.8-slim-buster

# Set working directory
ENV APP_HOME=/usr/src/app
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# Set envirovars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV development
ENV FLASK_APP blockchain.py

# Add and run as non-root user
RUN addgroup --system dock && \
    adduser --system --no-create-home --group dock
RUN chown -R dock:dock $APP_HOME && chmod -R 755 $APP_HOME

# Install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt $APP_HOME
RUN pip install -r requirements.txt

# Switch to non-root user
USER dock

# Add app
COPY . $APP_HOME

# Run the dev server
EXPOSE 5000
CMD flask run
