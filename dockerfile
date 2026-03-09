FROM python:3.13

WORKDIR /app

COPY requirements/ /app/requirements/
RUN pip install -r requirements/prod.txt

COPY . .

EXPOSE  8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]