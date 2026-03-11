FROM python:3.9
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "fb_bot.py"]
