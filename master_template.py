"""
PROJECT: <Name of Program>
PURPOSE: <Why you're writing this>
DATE: <Started on>
AUTHOR: <name of person writing program>

=============================
ORDER OF OPERATIONS (CHEAT SHEET)
=============================

[1] WHAT IS THE INPUT?
    - Describe all inputs. (source? type? limits?)
    - Examples:
      - user enters email
      - read CSV of stocks

[2] WHAT IS THE OUTPUT?
    - Exactly what should be returned, printed, exported?

[3] CONSTRAINTS?
    - speed? size? must handle missing data?
    - edge cases?

[4] RULES / LOGIC?
    - step-by-step logic in plain English
    - What must be true for success?

[5] WHAT LIBRARIES DO I NEED?
    - Built-in? External?
    - Why each one?

[6] SUB-TASKS / FUNCTIONS
    - Break the problem into small reusable pieces.
    - (You will implement them below.)

[7] TEST CASES
    - Write 3–5 tests BEFORE coding.
    - Example:
      valid email: "test@example.com"
      invalid email: "no-at-symbol"

"""

# =======================================
#  DEVELOPMENT STATUS TRACKER
# =======================================

# [YELLOW] QUESTIONS TO RESOLVE:
#   - 
#   - 

# [ORANGE] ANSWERS / DECISIONS:
#   - 
#   - 

# [GREEN] COMPLETED FEATURES:
#   - 
#   - 

# [BLUE] REFACTOR IDEAS (LATER):
#   - 
#   - 


# =======================================
#  IMPORTS
# =======================================
# import re
# import pandas as pd
# etc...

# =======================================
# GLOBAL CONSTANTS (optional)
# =======================================
# API_KEY = "..."
# MAX_THREADS = 8
# etc...

# =========================
# Helper Functions
# =========================
def load_data(path):
   """Load a CSV file safely."""
   return pd.read_csv(path)


def compute_something(x):
    """Example calculation function."""
    return x * 2

# 1. Input or configuration
    print("Program starting...")
    
    # 2. Load data
    # df = load_data("file.csv")
    
    # 3. Process data
    # result = compute_something(10)
    
    # 4. Output results
    # print(result)
    
    print("Done!")


# =======================================
#  MAIN FUNCTIONS
# =======================================
"""
def main():
    pass

    load the data
    clean the data
    calculate metrics
    filter the results
    export the results

As main() grows, you notice repeated logic or messy chunks.

That’s when you say:

“This part should be its own function.”

So you cut it out of main(), turn it into a helper function, and call it.

Example:

Before:

def main():
    df = pd.read_csv("file.csv")
    df.columns = [col.strip().lower() for col in df.columns]
    df.dropna(inplace=True)

After:

def main():
    df = load_data("file.csv")

and then you define:

def load_data(path):
    df = pd.read_csv(path)
    df.columns = [col.strip().lower() for col in df.columns]
    df.dropna(inplace=True)
    return df

3. Keep iterating — moving logic out of main() into helper functions.

Eventually main() becomes clean and readable:

def main():
    df = load_data("file.csv")
    df = clean_data(df)
    results = analyze(df)
    save_output(results)


if __name__ == "__main__":
    main()
"""