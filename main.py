import sys
from init_Database import ResetDatabase

if __name__=="__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "--init":
            print("Initializing the database...")
            ResetDatabase()
