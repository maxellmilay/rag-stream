FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV STREAMLIT_SERVER_HEADLESS true
ENV STREAMLIT_SERVER_PORT 8501
ENV STREAMLIT_SERVER_ADDRESS 0.0.0.0

RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py"]
