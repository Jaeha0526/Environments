from factorial import factorial

def test_factorial():
    try:
        assert factorial(1) == 1, f"factorial(1) is not {factorial(1)}"
        assert factorial(2) == 2, f"factorial(2) is not {factorial(2)}"
        assert factorial(3) == 6, f"factorial(3) is not {factorial(3)}"
        assert factorial(4) == 24, f"factorial(4) is not {factorial(4)}"
        assert factorial(5) == 120, f"factorial(5) is not {factorial(5)}"
        print("All tests passed!")
    except AssertionError as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_factorial()