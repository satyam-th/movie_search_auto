from robocorp.tasks import task


from excel import process_excel_file
from database import get_database_name, create_database_if_not_exists, insert_movie_data
from browser import search_and_extract_movie, browser

2

@task
def task():
    input_data = asking_user()

    if input_data[0] == "1":
        process_single_movie(input_data[1])

    elif input_data[0] == "2":
        process_excel_file(input_data[1])

    elif input_data[0] == "0":
        print("Exiting...")


def asking_user():
    print("Welcome to Movie Finder")
    num = input("1 = Single movie\n2 = Excel file\n0 = Exit\n> ")

    if num == "1":
        return (num, input("Enter movie: "))

    elif num == "2":
        return (num, input("Enter Excel file: "))

    elif num == "0":
        return (num, "")

    else:
        print("Invalid choice")
        return asking_user()


def process_single_movie(movie_name):
    print(f"\n--- Searching for {movie_name} ---")

    db_path = get_database_name(movie_name)
    create_database_if_not_exists(db_path)

    try:
        data = search_and_extract_movie(movie_name)
        insert_movie_data(db_path, data)
    except Exception as e:
        print("Error:", e)

    finally:
        browser.close_browser()
