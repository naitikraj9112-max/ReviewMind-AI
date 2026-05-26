import sqlite3
import time
import requests

# BAD: Hardcoded secrets
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def login_user(username, password):
    """
    Vulnerable login function with SQL Injection
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # BAD: SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    
    # BAD: Blocking performance issue (sleep inside auth)
    time.sleep(2)
    
    # BAD: Sending credentials over GET request
    requests.get(f"http://analytics.example.com/track?user={username}&pass={password}")
    
    return user

def process_data(data_list):
    """
    Vulnerable performance function
    """
    results = []
    # BAD: O(n^2) inefficient nested loops for large lists
    for item in data_list:
        for other_item in data_list:
            if item == other_item:
                results.append(item)
                
    # BAD: Catching general exception without logging
    try:
        1 / 0
    except Exception:
        pass
        
    return results
