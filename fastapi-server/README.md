# Setup a REST API server on GCP for a Langroid script

:warning: See the [langroid/fastapi-server](https://github.com/langroid/fastapi-server) repo for a more comprehensive and up-to-date example.

Ensure that your env secrets are in this folder as a `.env` file.
We will of course *not* include it in the docker image
(which is why it's in the `.dockerignore` file) but we will use it
for local testing by passing this file in as an env file to the uvicorn server.
(See the defn of `make run` in the Makefile.)

## local testing

Build server using `make server`, run it with `make run`.
See the definitions of these in the Makefile. Notice that 
we are passing in the env variables

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

`process_file_and_data` endpoint:

```bash
curl -X POST "http://localhost:8000/process_file_and_data/" \
     -F "file=@/tmp/query.txt" \
     -F 'complex_data={"id": 1, "item": {"name": "Item Name", "description": "A description", "quantity": 10, "tags": ["tag1", "tag2"]}, "related_items": [{"name": "Related Item 1", "description": "Description 1", "quantity": 5, "tags": ["tag3", "tag4"]}, {"name": "Related Item 2", "description": "Description 2", "quantity": 3, "tags": ["tag5", "tag6"]}]}'
```

## Deploy to google cloud run

Below are the rough steps, I may have forgotten some.

Ensure docker, google cloud cli are installed.

See other details here:
https://chat.openai.com/share/c34583c8-b88e-4a70-bf24-83229700c020


Run `make gserver`, `make gpush` from within the dir where the Dockerfile is 
located.

Go to Google Cloud Run Service and create a new service, 
selecting the latest version of the pushed docker image above, e.g.: 
`gcr.io/langroid/langroid-server:latest`

When setting up the service:
- ensure you select the same port number as in the Dockerfile, e.g. 80.
- set up environment variables such as `OPENAI_API_KEY`, etc. *Do not include a 
 .env file containing secret keys in the docker image!* We've included `.env` 
 in the `.dockerignore` file to prevent this.

If the service fails to start due to an error like `uvicorn: exec format error`, 
then you may be able to fix it by explicitly choosing an architecture 
in the Dockerfile, e.g. `linux/amd64` (which we chose in the Dockerfile).

### Creating secrets in google cloud
Some commands for quick reference:

```bash
gcloud secrets create openai-api-key --replication-policy="automatic"
echo -n "your-openai-api-key" | gcloud secrets versions add openai-api-key --data-file=-
```

After creating your secret and adding its value, you may need to set appropriate 
permissions for the secret. Use gcloud secrets add-iam-policy-binding to grant access 
to the secret:

```bash
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:langroid-docai-sa@langroid.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

To expose one of these as environment var named `OPENAI_API_KEY` in the cloud run 
service:

```bash
gcloud run services update langroid-server \
 --update-secrets OPENAI_API_KEY=openai-api-key:latest \
 --region=us-east4
```

## Test GCP endpoints

Same curl cmds as above, but use the endpoint url from the GCP Cloud Run service, 
e.g. (Note: You must *not* provide a port number in the url!).
```bash
https://langroid-server-xxxxx-uc.a.run.app/process_text
https://langroid-server-xxxxx-uc.a.run.app/process_file
```
