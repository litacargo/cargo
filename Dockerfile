FROM python:3.11
WORKDIR /app/cargo
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN python manage.py collectstatic --noinput
EXPOSE 8000
COPY entrypoint.sh /entrypoint.sh 
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]