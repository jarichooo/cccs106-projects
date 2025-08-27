# CCCS 106 - Week 1 Lab Exercise
# Simple Interactive Calculator

print("=" * 40)
print("ENHANCED BASIC CALCULATOR")
print("=" * 40)

# Get user input
print("Enter two numbers for calculation:")
try:
    num1 = float(input("First number: "))
    num2 = float(input("Second number: "))
    
    # Perform calculations
    addition = num1 + num2 
    subtraction = num1 - num2 
    multiplication = num1 * num2
    power = num1**num2 # powers the first integer by the second number
    sqrt1 = num1**0.5 # squareroot of the first int
    sqrt2 = num2**0.5 # squareroot of the second int 
    
    # Handle division by zero
    if num2 != 0:
        division = num1 / num2
    else:
        division = "Cannot divide by zero"
    
    # Display results
    print("\n" + "=" * 40)
    print("RESULTS:")
    print("=" * 40)
    print(f"{num1} + {num2} = {addition}")
    print(f"{num1} - {num2} = {subtraction}")
    print(f"{num1} * {num2} = {multiplication}")
    print(f"{num1} / {num2} = {division}")
    print(f"{num1} ^ {num2} = {power}")
    print(f"_/ {num1} = {sqrt1}")
    print(f"_/ {num2} = {sqrt2}")
    
    # Additional information
    print(f"\nLarger number: {max(num1, num2)}")
    print(f"Smaller number: {min(num1, num2)}")
    
except ValueError:
    print("Error: Please enter valid numbers only!")
except Exception as e:
    print(f"An error occurred: {e}")

print("\nThank you for using Basic Calculator!")