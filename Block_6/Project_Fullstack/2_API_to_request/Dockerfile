FROM n0rdinateur/ubuntu-opencv-dlib-for-jedha:latest

WORKDIR /home/app

COPY requirements.txt /dependencies/requirements.txt

RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV BACKEND_STORE_URI=$BACKEND_STORE_URI
ENV ARTIFACT_STORE_URI=$ARTIFACT_STORE_URI

CMD gunicorn app:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker