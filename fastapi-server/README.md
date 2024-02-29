# Setup a REST API server on GCP for a Langroid script

## local testing

Build server using `make server`, run it with `make run`

## Curl examples to test the server locally

`process_text` endpoint:

```bash
curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"text": "capital of hungary?"}' \
     http://localhost/process_text
```

`process_file` endpoint:

```bash
curl -X POST \
    -F "file=@/tmp/query.txt" \
    -o out.txt \ 
    http://localhost/process_file
```
(If you omit the `-o out.txt` part, the response will be printed to the terminal.)


## Deploy to google cloud run

Below are the rough steps, I may have forgotten some.

Ensure docker, google cloud cli are installed.

See other details here:
https://chat.openai.com/share/c34583c8-b88e-4a70-bf24-83229700c020


Run these from within the dir where the Dockerfile is located:

```bash
gcloud auth configure-docker
docker build -t gcr.io/langroid/langroid-server:v1 .
docker push  gcr.io/langroid/langroid-server:v1
```

The `build` and `push` cmds are also available via the Makefile 
as `make gbuild` and `make gpush` respectively.

Go to Google Cloud Run Service and create a new service, 
selecting the latest version of the pushed docker image above: 
`gcr.io/langroid/langroid-server:v1`

When setting up the service:
- ensure you select the same port number as in the Dockerfile, e.g. 80.
- set up environment variables such as `OPENAI_API_KEY`, etc. *Do not include a 
 .env file containing secret keys in the docker image!* We've included `.env` 
 in the `.dockerignore` file to prevent this.

If the service fails to start due to an error like `uvicorn: exec format error`, 
then you may be able to fix it by explicitly choosing an architecture 
in the Dockerfile, e.g. `linux/amd64` (which we chose in the Dockerfile).

## Test GCP endpoints

Same curl cmds as above, but use the endpoint url from the GCP Cloud Run service, 
e.g.
```bash
https://langroid-server-xxxxx-uc.a.run.app/process_text
https://langroid-server-xxxxx-uc.a.run.app/process_file
```
