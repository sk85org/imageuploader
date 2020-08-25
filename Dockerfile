FROM python:latest
ARG img_dir=/img
ARG app_dir=/app
WORKDIR $app_dir
RUN pip install flask uWSGI pymongo
CMD ["uwsgi", "uwsgi.ini"]
EXPOSE 8080