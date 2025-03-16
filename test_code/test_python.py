#!/usr/bin/env python3

# This is a utility function for string manipulation
# It reverses the input string
def reverse_string(s):
    """
    Reverses the characters in a string.
    
    Args:
        s (str): The input string to reverse
        
    Returns:
        str: The reversed string
    """
    return s[::-1]

# This class handles mathematical operations
class Calculator:
    """
    A simple calculator class that provides basic arithmetic operations.
    """
    
    def __init__(self, initial_value=0):
        self.value = initial_value
    
    # Adds a number to the current value
    def add(self, x):
        """Adds x to the current value"""
        self.value += x
        return self.value
    
    # Subtracts a number from the current value
    def subtract(self, x):
        """Subtracts x from the current value"""
        self.value -= x
        return self.value
