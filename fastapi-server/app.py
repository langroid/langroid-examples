from typing import Any
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
import langroid as lr


class TextInput(BaseModel):
    text: str

class Server:
    def __init__(self):
        self.setup()

    def setup(self):
        # Perform your potentially expensive initial setup here
        self.agent = lr.ChatAgent()

    def serve_text(self, text:str) -> str:
        result = self.agent.llm_response(text)
        return result.content

    def serve_file(self, text_content: str, filename: str) -> str:
        # Answer the query, put response in a file and return it
        result = self.agent.llm_response(text_content)
        output_filename = f"processed_{filename}"
        with open(output_filename, 'w') as f:
            f.write(result.content)
        return output_filename


app = FastAPI()
server = Server()

@app.post("/process_file", response_class=FileResponse)
async def process_file(file: UploadFile = File(...)) -> Any:
    try:
        # Read file content and decode to text
        file_content_bytes = await file.read()
        text_content = file_content_bytes.decode('utf-8')
        # Process text and get the path to the output file
        output_filename = server.serve_file(text_content, file.filename)
        return FileResponse(
            path=output_filename,
            filename=output_filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    #TODO: Omit the file cleanup since we need to return the file
    # finally:
    #     # Cleanup by removing the created output file if necessary
    #     if os.path.exists(output_filename):
    #         os.remove(output_filename)

@app.post("/process_text")
def process_text(text_input: TextInput) -> Any:
    result = server.serve_text(text_input.text)
    return {"message": result, "status": "ok"}

# This port number must match the port number in the Dockerfile
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
