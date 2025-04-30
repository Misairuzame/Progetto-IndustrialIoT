FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk add tzdata
RUN ln -s /usr/share/zoneinfo/Europe/Rome /etc/localtime

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY elaboration.py .

CMD ["python", "elaboration.py"]
