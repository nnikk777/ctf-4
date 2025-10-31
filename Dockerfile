FROM python:3.9-slim-bullseye  

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN touch /tmp/waiting_list.txt

EXPOSE 5000
CMD ["python", "app.py"]