from typing import Any, Dict, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Json
import uvicorn
import os
import langroid as lr


class TextInput(BaseModel):
    text: str

# Define your Pydantic models for the complex payload
class Item(BaseModel):
    name: str
    description: str
    quantity: int
    tags: List[str]

class ComplexItem(BaseModel):
    id: int
    item: Item
    related_items: List[Item]


class Server:
    def __init__(self):
        self.setup()

    def setup(self):
        # Perform your potentially expensive initial setup here
        self.agent = lr.ChatAgent()

    def serve_text(self, text:str, key:str|None=None) -> str:
        os.environ["OPENAI_API_KEY"] = key or "xxx"
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


# Dependency for API Key authentication
async def extract_api_key(request: Request) -> str:
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid scheme in Authorization header"
            )
        return token
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format"
        )

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
    api_key = os.environ.get("OPENAI_API_KEY")
    result = server.serve_text(text_input.text, key=api_key)
    return {"message": result, "status": "ok"}

# authenticated example
@app.post("/process_text_auth")
def process_text(
    text_input: TextInput,
    api_key:str = Depends(extract_api_key),
) -> Any:
    result = server.serve_text(text_input.text, key=api_key)
    return {"message": result, "status": "ok"}

@app.post("/process_file_and_data/")
async def process_file_and_data(
    file: UploadFile = File(...),
    complex_data: Json[ComplexItem] = Form(...)
) -> Dict[str, Any]:
    # You can now access the file and the complex data
    # For example, save the file and process the complex data
    # Here, just return a message indicating success for demonstration

    return {
        "message": "Received file and complex data successfully!",
        "file_name": file.filename,
        "complex_data_id": complex_data.id,
        "complex_data_item_name": complex_data.item.name
    }

# This port number must match the port number in the Dockerfile
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
