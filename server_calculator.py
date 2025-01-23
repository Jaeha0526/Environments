from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import Optional, Literal
from enum import Enum

# Initialize FastAPI application
app = FastAPI(title="Advanced Calculator API")

# Define our request model for two numbers
class Numbers(BaseModel):
    num1: float
    num2: float

# Define our request model for a list of numbers
class NumbersList(BaseModel):
    numbers: list[float]
    
# Define supported operations for clarity
class Operation(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"

@app.get("/")
async def root():
    """Root endpoint that confirms the API is running and shows available operations"""
    return {
        "message": "Calculator API is running",
        "available_operations": [
            "/calculate/{operation} - Performs basic arithmetic (add, subtract, multiply, divide)",
            "/sum - Sums a list of numbers",
            "/average - Calculates the average of a list of numbers"
        ]
    }

@app.post("/calculate/{operation}")
async def calculate(operation: Operation, numbers: Numbers):
    """
    Unified endpoint for basic arithmetic operations
    
    Args:
        operation: The arithmetic operation to perform
        numbers: Two numbers to operate on
    """
    try:
        if operation == Operation.ADD:
            result = numbers.num1 + numbers.num2
        elif operation == Operation.SUBTRACT:
            result = numbers.num1 - numbers.num2
        elif operation == Operation.MULTIPLY:
            result = numbers.num1 * numbers.num2
            
        return {
            "operation": operation,
            "num1": numbers.num1,
            "num2": numbers.num2,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sum")
async def sum_numbers(numbers: NumbersList):
    """
    Calculates the sum of a list of numbers
    
    Args:
        numbers: List of numbers to sum
    """
    result = sum(numbers.numbers)
    return {
        "operation": "sum",
        "numbers": numbers.numbers,
        "result": result
    }

@app.post("/average")
async def calculate_average(numbers: NumbersList):
    """
    Calculates the average (mean) of a list of numbers
    
    Args:
        numbers: List of numbers to average
    """
    if not numbers.numbers:
        raise HTTPException(status_code=400, detail="Cannot calculate average of empty list")
    
    result = sum(numbers.numbers) / len(numbers.numbers)
    return {
        "operation": "average",
        "numbers": numbers.numbers,
        "result": result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9003)