# Lab 7 – Python Testing

**Student:** Haya Karanouh  
**Course:** EECE 435 – Software Tools Lab  
**Submission:** Lab7-Haya-Karanouh

## Run the project

Use Python 3.10 or later. The submitted tests were verified with Python 3.14.3.

```bash
cd Lab7-Haya-Karanouh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
```

On Windows, activate with `.venv\Scripts\activate` instead.
No running Flask server or Postman is needed: API tests use Flask's test client.
To run the application manually, use `python app.py`.
The original Lab 5 Postman collection is included for reference.

## Graded activity

`test_user_Haya_Karanouh.py` contains 25 tests covering all ten requirements.
The application and database modules are copied unchanged from the Lab 5 project:
<https://github.com/haya-karanouh/Lab5-435--HayaKaranouh->.

| Lab requirement | Main test |
| --- | --- |
| 1. Database created with specified users on the first app run | `test_database_created_with_specified_users_on_first_app_run` |
| 2. Insert_user() | `test_insert_user` |
| 3. Get_users() | `test_get_users` |
| 4. Get_users_by_id() | `test_get_user_by_id` |
| 5. Update_user() | `test_update_user` |
| 6. Delete_user() | `test_delete_user` |
| 7. Api_get_user() | `test_api_get_user`, `test_api_get_users` |
| 8. Api_add_user() | `test_api_add_user` |
| 9. Api_update_user() | `test_api_update_user` |
| 10. Api_delete_user() | `test_api_delete_user` |

The PDF uses conceptual function names. The tests call the existing Lab 5
functions (`get_user_by_id`, for example) and its actual HTTP routes.

Each test receives its own temporary SQLite database through pytest fixtures.
The startup test imports the application in a fresh Python process in a temporary
directory and checks that `database.db` is created with all three original seed
users and their exact fields. Another test checks that initialization preserves
existing data without duplicating seeds.

Database write tests independently read SQLite to check persistence and unaffected
records. API tests verify both HTTP status codes and complete JSON bodies, compare
uploaded and downloaded values, and check stored changes. Additional tests cover
missing users, missing required fields, invalid user IDs, non-JSON input, an empty
table, and repeated deletion. Test data uses example.com addresses.

```bash
python -m pytest -v test_user_Haya_Karanouh.py
```

## Other lab exercises

- `capitalize.py` and `test_capitalize.py`: capitalization, the friendly TypeError,
  and support for string subclasses (3 tests).
- `wallet.py` and `test_wallet.py`: the five wallet tests refactored with
  `empty_wallet` and `wallet` fixtures, including insufficient funds (5 tests).
- `hello_add.py` and `test_hello_add.py`: POST `/add` returns HTTP 200 and
  `{"sum": 3}` for `{"a": 1, "b": 2}` (1 test).

## Verification and submission

**Result: 34 passed** (25 graded-activity tests and 9 tutorial tests).

`screenshots/` contains actual captures of successful terminal runs.
`test-results/` contains the corresponding text output and JUnit XML report.

Upload `Lab7-Haya-Karanouh.zip` and the main successful-run screenshot
`screenshots/01-all-tests-passed.png` to Moodle as requested by the lab.
The archive includes the screenshot folder as well. A virtual environment and
runtime databases are intentionally excluded; the application creates its
database automatically, and tests always create isolated databases.
