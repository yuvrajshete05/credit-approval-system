FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["gunicorn", "credit_approval_system.wsgi:application", "--bind", "0.0.0.0:8000"]
