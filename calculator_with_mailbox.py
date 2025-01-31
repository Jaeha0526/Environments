from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List
import asyncio
from datetime import datetime
import uvicorn

app = FastAPI(title="Calculator with Mailbox API")

# In-memory storage for our mailbox
mailbox = {}
job_id = 0

# Models for request validation
class MultiplicationInput(BaseModel):
    num1: int
    num2: int
    
    @validator('num1', 'num2')
    def validate_digits(cls, v):
        # Limit numbers to 4 digits
        if abs(v) > 9999:
            raise ValueError("Numbers must be 4 digits or less")
        return v


class SummationInput(BaseModel):
    numbers: List[int] = Field(..., description="List of numbers to sum")


# Mailbox operations
def write_to_mailbox(job_id: int, operation: str, input: List, result: float):
    """Write a result to the mailbox with timestamp"""
    if operation == "multiplication":
        mailbox[f"{job_id}"] = f"Multiplication of {input[0]} and {input[1]} is {result}."
    elif operation == "summation":
        mailbox[f"{job_id}"] = f"Summation of {input} is {result}."
    return

@app.get("/")
async def root():
    """Root endpoint that shows available operations"""
    return {
        "message": "Calculator API with Mailbox is running",
        "available_operations": [
            "/multiply - Limited-digit multiplication (max 4 digits)",
            "/sum - Sum any number of values",
            "/mailbox - View mailbox contents",
        ]
    }

@app.post("/multiply")
async def multiply(numbers: MultiplicationInput):
    """
    Multiply two numbers (max 4 digits each) and store result in mailbox after 3 seconds
    """
    try:
        global job_id
        
        # Allocate job ID
        current_job_id = job_id
        job_id += 1
        
        # Calculate result
        result = numbers.num1 * numbers.num2
        input = [numbers.num1, numbers.num2]
        
        # Schedule delayed write to mailbox
        async def delayed_write():
            await asyncio.sleep(1)  # 1 second delay
            write_to_mailbox(current_job_id, "multiplication", input, result)
            print(f"Multiplication done. Result: {result}")
            
        # Start the delayed write task
        asyncio.create_task(delayed_write())
        
        # Return immediately with job_id
        return {
            "status": "success",
            "message": f"Multiplication scheduled. Result will be available in mailbox index {current_job_id} after 3 seconds.",
            "mailbox_index": current_job_id
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/sum")
async def sum_numbers(numbers: SummationInput):
    """
    Sum a list of numbers and store result in mailbox after 3 seconds
    """
    try:
        # Calculate result
        result = sum(numbers.numbers)
        input = numbers.numbers
        
        global job_id
        
        # Allocate job ID
        current_job_id = job_id
        job_id += 1
        
        # Schedule delayed write to mailbox
        async def delayed_write():
            await asyncio.sleep(1)  # 1 second delay
            write_to_mailbox(current_job_id, "summation", input, result)
            print(f"Summation done. Result: {result}")
            
        # Start the delayed write task
        asyncio.create_task(delayed_write())
        
        # Return immediately with job_id
        return {
            "status": "success",
            "message": f"Summation scheduled. Result will be available in mailbox index {current_job_id} after 3 seconds.",
            "mailbox_index": current_job_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/mailbox")
async def get_mailbox():
    """
    Retrieve all entries from the mailbox
    """
    return mailbox

@app.get("/mailbox/{index}")
async def get_mailbox_entry(index: int):
    """
    Retrieve a specific entry from the mailbox
    """
    try:
        entry = mailbox.get(str(index))
        if entry is None:
            return {
                "status": "error",
                "entry": f"No entry found at index {index}"
            }
            # raise HTTPException(status_code=404, detail=f"No entry found at index {index}")
        return {
            "status": "success",
            "entry": entry
        }
    except Exception as e:
        return {
            "status": "error",
            "entry": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9012)