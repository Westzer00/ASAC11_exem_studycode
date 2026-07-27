import os

from dotenv import load_dotenv


load_dotenv()


def main():
    app_name = os.getenv("APP_NAME")
    api_key = os.getenv("API_KEY")

    print("APP_NAME:", app_name)
    print("API_KEY:", api_key)


if __name__ == "__main__":
    main()