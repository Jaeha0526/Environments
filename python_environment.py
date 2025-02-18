from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os

app = FastAPI(title="VM Python Execution Environment")

# Directory for storing Python scripts
CODE_DIR = "./code_repository"
TEST_FILE = "./code_repository/test_factorial.py"
os.makedirs(CODE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(TEST_FILE), exist_ok=True)

class CodeUpdateRequest(BaseModel):
    code: str

class ExecutionRequest(BaseModel):
    input_value: int

@app.get("/files/{filename}")
def get_code(filename: str):
    """Fetch the current code from the repository"""
    filepath = os.path.join(CODE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    with open(filepath, "r") as f:
        return {"filename": filename, "code": f.read()}

@app.put("/files/{filename}")
def update_code(filename: str, request: CodeUpdateRequest):
    """Update the Python script in the repository"""
    filepath = os.path.join(CODE_DIR, filename)
    with open(filepath, "w") as f:
        f.write(request.code)
    return {"message": "Code updated successfully", "filename": filename}

@app.post("/execute/{filename}")
def execute_code(filename: str, request: ExecutionRequest):
    """Execute a script with input and return the output"""
    filepath = os.path.join(CODE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = subprocess.run(["python", filepath], input=str(request.input_value), capture_output=True, text=True, timeout=5)
        return {"stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/execute_test")
def execute_test():
    """Execute the predefined test script and return detailed results"""
    if not os.path.exists(TEST_FILE):
        raise HTTPException(status_code=404, detail="Test file not found")
    
    try:
        result = subprocess.run(["python", TEST_FILE], capture_output=True, text=True, timeout=5)
        output = result.stdout.strip()
        error = result.stderr.strip()

        if error:
            return {"error": error}
        
        failures = []
        for line in output.split("\n"):
            if "FAILED" in line:
                failures.append(line)
        
        return {"stdout": output, "failures": failures}
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9019)
