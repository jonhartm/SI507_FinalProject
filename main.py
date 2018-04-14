import sys

if __name__=="__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "--init":
            print("initialize the database")
