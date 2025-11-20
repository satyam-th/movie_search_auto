from RPA.Excel.Files import Files
from browser import search_and_extract_movie, browser
from database import (
    get_database_name,
    create_database_if_not_exists,
    insert_movie_data
)

def process_excel_file(file_name):
    excel = Files()
    excel.open_workbook(file_name)

    rows = excel.read_worksheet_as_table(header=True)
    print(f"Processing {len(rows)} movies...\n")

    for row in rows:
        movie_name = row.get("Movie") or list(row.values())[0]

        print(f"Processing: {movie_name}")

        db_path = get_database_name(movie_name)
        create_database_if_not_exists(db_path)

        try:
            data = search_and_extract_movie(movie_name)
            insert_movie_data(db_path, data)
        except Exception as e:
            print("Error:", e)
            insert_movie_data(db_path, {"movie_name": movie_name, "status": f"Error: {e}"})

    excel.close_workbook()
    browser.close_browser()
