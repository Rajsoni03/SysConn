# src/utils/exception.py
'''
Custom exception classes for the application.
'''

class UartSetupIssue(Exception):
    """Exception raised for errors in the UART setup."""
    pass