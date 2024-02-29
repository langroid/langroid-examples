LOCAL_ARCH=$(shell uname -m)
GCLOUD_ARCH=amd64
IMAGE_NAME=langroid-server
TAG=latest

server:
	docker build --platform linux/$(LOCAL_ARCH) -t $(IMAGE_NAME):$(TAG) .

run:
	docker run --env-file .env -d -p 80:80 $(IMAGE_NAME):$(TAG)

stop:
	docker stop $(shell docker ps -q)

gserver:
	docker build --platform=linux/$(GCLOUD_ARCH) -t gcr.io/langroid/$(IMAGE_NAME):$(TAG) .

gpush:
	docker push gcr.io/langroid/$(IMAGE_NAME):$(TAG)