FROM python:3.10.2
ARG img_dir=/img
ARG app_dir=/app
WORKDIR $app_dir
RUN pip install flask uWSGI pymongo==4.1.1
CMD ["uwsgi", "uwsgi.ini"]
EXPOSE 8080