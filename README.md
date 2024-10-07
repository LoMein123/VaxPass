# Ontario Vaccine Passport (VaxPass)

A vaccine passport web application for the province of Ontario built using the Flask framework. The app allows medical professionals to update the vaccination record of their patients. The patients are then able to generate a unique QR code which displays their vaccination status. This QR code can then be scanned by businesses to allow or disallow entry to their premises. Other information about each vaccination such as the vaccine type and the dose administrator are stored in the database.

Nurses can register or log in to administer vaccine doses to users. Nurses can record which vaccine they have just administered to which patient and the system will update the patient's information through connection to the
provincial database.

Users (patients) can log into their accounts to generate QR codes that contain information about their vaccination status.

### Root folder holds all the files and folders needed in the application:
- `<app.py>` contains all the code for the backend.
- `<helpers.py>` contains helper functions for `app.py`.
- `<vaccine.db>` is a database which stores all information required for the app.

### Templates folder holds all the html files:
- `<login.html>` is the patient login page.
- `<register.html>` is the patient registration page.
- `<index.html>` is the patient dashboard page for patients to check their vaccination status and generate QR codes with their vaccination status.

- `<nurselogin.html>` is the nurse login page.
- `<registernurse.html>` is the nurse registration page.
- `<admin.html>` is intermediate page for nurses to enter a patients health card. 
- `<admincentre.html>` is a page for nurses to administer a vaccine to the given patient.

- `<layout.html>` contains templates for for header and footer.
- `<error.html>` displays error code and message.

### Static folder holds all the image assets and stylesheets


# How to run
1. Clone the repository.
2. In the terminal, use the command: `pip install -r requirements.txt`.
3. Move to the directory the project is cloned to, then use the command: `flask run`.