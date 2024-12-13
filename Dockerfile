FROM python:3.9-slim
WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8500

CMD ["streamlit", "run", "__main__.py", "--server.port=8500", "--server.address=0.0.0.0"]