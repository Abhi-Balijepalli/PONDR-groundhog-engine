# from models import run_models
import subprocess, os



def main():

    # subprocess.run(['C:\ProgramData\Anaconda3\envs\BananasReviews\python.exe', 'C:/Users/tomcs/Desktop/BananasReviews/reviews.py'], shell=True)
    #  subprocess.run(['C:\ProgramData\Anaconda3\envs\GPT2-testing\python.exe', 'C:/Users/tomcs/Desktop/BananasReviews/GPT2.py'], shell=True)
    subprocess.run(['C:\ProgramData\Anaconda3\envs\BananasReviews\python.exe', 'C:/Users/tomcs/Desktop/BananasReviews/models.py'], shell=True)
    #  subprocess.run(['C:\ProgramData\Anaconda3\envs\BananasReviews\python.exe', 'C:/Users/tomcs/Desktop/BananasReviews/api.py'], shell=True)

if __name__ == "__main__":
    main()
