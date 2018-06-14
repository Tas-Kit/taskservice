FROM python:2
ENV PYTHONUNBUFFERED 1
RUN mkdir /taskservice
WORKDIR /taskservice
ADD requirements.txt /taskservice/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y gettext nano
ADD . /taskservice/
CMD python manage.py runserver
