FROM python

WORKDIR /home/app

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

CMD gunicorn getaround_app_predictor:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker