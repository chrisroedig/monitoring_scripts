FROM python:3

# set a directory for the app
WORKDIR /app

# copy all the files to the container
COPY . .

# add the config to the /data volume
ADD config.yml /data/config.yml

ENV CONFIG_FILE /data/config.yml

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "./run_schedule.py"]
