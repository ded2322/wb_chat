FROM python:3.10

RUN mkdir /core
WORKDIR /core

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /core/static/original_images
RUN mkdir -p /core/static/image_default
RUN mkdir -p /core/static/resize_images
RUN mkdir -p /core/logs/

COPY core/static /core/static

EXPOSE 8000

CMD ["uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000"]
