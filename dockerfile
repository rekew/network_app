FROM python:3.13

WORKDIR /app

COPY requirements/ /app/requirements/
RUN pip install -r requirements/prod.txt

COPY . .

EXPOSE  8000

CMD ["gunicorn", "settings.wsgi:application", "--bind", "0.0.0.0:8000"]