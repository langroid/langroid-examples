server:
	docker build -t server .

run:
	docker run -d -p 80:80 server

stop:
	docker stop $(shell docker ps -q)

gbuild:
	docker build -t gcr.io/langroid/langroid-server:v1 .

gpush:
	docker push gcr.io/langroid/langroid-server:v1