from datetime import datetime

from flask import Flask, request, render_template, send_file, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
import pandas as pd
import google.generativeai as genai
from io import BytesIO
import json
from types import SimpleNamespace
from database import init_db, save_to_db, fetch_from_db, save_user, find_user, import_emissions
import xlsxwriter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['DOWNLOAD_FOLDER'] = 'DataBase_downloaded'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.secret_key = os.urandom(24)

# Ваш API-ключ Google
os.environ['mykey'] = "AIzaSyBJ2VMOr2zu6InzIz9E8pmx247eAJ6b2X4" 
genai.configure(api_key=os.environ["mykey"])
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)
init_db()
list_of_dicts = import_emissions()
type_id_to_co2 = {
        1: 8.27,
        2: 6.25,
        3: 3.92,
        4: 0.63,
        6: 2.25,
        7: 0.98,
        8: 2.50,
        9: 0.292,
        10: 0.70,
        11: 16.00,
        12: 0.3,
        13: 0.18,
        14: 0.80,
        15: 0.025,
        16: 0.25,
        17: 0.33,
        18: 1.20,
        19: 8.51,
        20: 1.55,
        21: 8.1,
        22: 1.18,
        23: 1.00,
        24: 6.07,
        25: 0.3,
        26: 2.71,
        27: 1166.67,
        28: 6.73,
        30: 0.4,
        32: 0.309
    }

DATABASE = "invoices.db"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template('index.html', invoices= fetch_from_db(), message=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect('/login')

    files = request.files.getlist('files')
    all_data = []

    jsonData = "[{\"typeid\":1,\"Type_Name\":\"FOOD\",\"Type_Decode_LV\":\"Pārtikas izstrādājumi\",\"Mērvienība\":\"kg / vienība\"},{\"typeid\":2,\"Type_Name\":\"CHOC\",\"Type_Decode_LV\":\"Šokolādes izstrādājumi\",\"Mērvienība\":\"kg\"},{\"typeid\":3,\"Type_Name\":\"TEL\",\"Type_Decode_LV\":\"Komunikācijas pakalpojumi\",\"Mērvienība\":\"mēn. / vienība\"},{\"typeid\":4,\"Type_Name\":\"TOOL\",\"Type_Decode_LV\":\"Instrumenti\",\"Mērvienība\":\"vienības\"},{\"typeid\":6,\"Type_Name\":\"GAS\",\"Type_Decode_LV\":\"Gāze\",\"Mērvienība\":\"l\"},{\"typeid\":7,\"Type_Name\":\"ELEC\",\"Type_Decode_LV\":\"Elektrība\",\"Mērvienība\":\"kWh/vienība\"},{\"typeid\":8,\"Type_Name\":\"FUEL\",\"Type_Decode_LV\":\"Degviela\",\"Mērvienība\":\"l\"},{\"typeid\":9,\"Type_Name\":\"OFF\",\"Type_Decode_LV\":\"Kancelejas preces\",\"Mērvienība\":\"vienība\"},{\"typeid\":10,\"Type_Name\":\"BEER\",\"Type_Decode_LV\":\"Alus\",\"Mērvienība\":\"l\"},{\"typeid\":11,\"Type_Name\":\"COSM\",\"Type_Decode_LV\":\"Kosmetikas piederumi\",\"Mērvienība\":\"vienība\"},{\"typeid\":12,\"Type_Name\":\"TRAV\",\"Type_Decode_LV\":\"Ceļojumi\",\"Mērvienība\":\"vienība\"},{\"typeid\":13,\"Type_Name\":\"POST\",\"Type_Decode_LV\":\"Pasta pakalpojumi\",\"Mērvienība\":\"vienība\"},{\"typeid\":14,\"Type_Name\":\"DAIRY\",\"Type_Decode_LV\":\"Piena pārtika\",\"Mērvienība\":\"kg/l\"},{\"typeid\":15,\"Type_Name\":\"WOOD\",\"Type_Decode_LV\":\"Koka izstrādājumi\",\"Mērvienība\":\"m3\"},{\"typeid\":16,\"Type_Name\":\"PHAR\",\"Type_Decode_LV\":\"Medikamenti\",\"Mērvienība\":\"vienība\"},{\"typeid\":17,\"Type_Name\":\"GLASS\",\"Type_Decode_LV\":\"Stikla izstrādājumi\",\"Mērvienība\":\"kg\"},{\"typeid\":18,\"Type_Name\":\"ENT\",\"Type_Decode_LV\":\"Ūdens izklaides pakalpojumi\",\"Mērvienība\":\"vienība\"},{\"typeid\":19,\"Type_Name\":\"CLOTH\",\"Type_Decode_LV\":\"Tekstīla izstrādājumi\",\"Mērvienība\":\"vienība\"},{\"typeid\":20,\"Type_Name\":\"ALCO\",\"Type_Decode_LV\":\"Alkohola dzērieni\",\"Mērvienība\":\"l/vienība\"},{\"typeid\":21,\"Type_Name\":\"CONST\",\"Type_Decode_LV\":\"Celtniecības pakalpojumi\",\"Mērvienība\":\"t/vienība\"},{\"typeid\":22,\"Type_Name\":\"TRANS\",\"Type_Decode_LV\":\"Transportēšanas pakalpojumi\",\"Mērvienība\":\"l/t/vienība\"},{\"typeid\":23,\"Type_Name\":\"RETAIL\",\"Type_Decode_LV\":\"Pārdošanas pakalpojumi\",\"Mērvienība\":\"vienība\"},{\"typeid\":24,\"Type_Name\":\"METAL\",\"Type_Decode_LV\":\"Metalurģijas izstrādājumi\",\"Mērvienība\":\"t/vienība\"},{\"typeid\":25,\"Type_Name\":\"HOME\",\"Type_Decode_LV\":\"Mājas apsaimniekošanas pakalpojumi\",\"Mērvienība\":\"mēn\"},{\"typeid\":26,\"Type_Name\":\"OIL\",\"Type_Decode_LV\":\"Naftas izstrādājumi\",\"Mērvienība\":\"l\"},{\"typeid\":27,\"Type_Name\":\"RECYCLE\",\"Type_Decode_LV\":\"Pārstrādes pakalpojumi\",\"Mērvienība\":\"t\"},{\"typeid\":28,\"Type_Name\":\"INS\",\"Type_Decode_LV\":\"Apdrošināšanas pakalpojumi\",\"Mērvienība\":\"vienība\"},{\"typeid\":30,\"Type_Name\":\"TICKET\",\"Type_Decode_LV\":\"Izklaides pakalpojumi\",\"Mērvienība\":\"vienība\"},{\"typeid\":32,\"Type_Name\":\"HEAT\",\"Type_Decode_LV\":\"Apkures pakalpojumi\",\"Mērvienība\":\"kWh\"}]"

    for file in files:
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Вызов Google API для обработки данных
            with open(filepath, "rb") as file_content:
                myfile = genai.upload_file(filepath)
                result = model.generate_content([ 
                    myfile,
                    "\n\nAtrodi datus no rēķina"
                    "(Tikai datumu date, kompāniju company, produktu name, daudzumu quantity, cenu price un 2 paplidus parametrus,"
                    " kas nav dokumentā un kurus vajag saskitīt - typeid un correcyQuantity.)"
                    " un atdod tos JSON formātā bez paskaidrojumiem vai papildus teksta.\n\n"
                    "Atbildi sniedz vienā līmenī, kur katrs ieraksts ir JSON objekts, kas atrodās json massīvā, piemēram:\n"
                    "[{"
                 "\"date\": \"DD/MM/YYYY\","
                 "\"company\": \"firma\","
                 "\"name\": \"produkts\","
                 "\"quantity\": daudzums,"
                 "\"price\": cena,"
                 "\"typeid\": typeid no pielikta tālāk JSON,"
                 "\"correctQuantity\": daudzums mervenībā no pielikat tālāk Json (ja jsonā ir mērvieniba 1 kg, bet failā 1 tona, tad jākonvertē daudzumu, kas rakstīts failā uz mērvienību, kas rakstīts JSON)"
                 "}] Rekur json: "+ jsonData +
                    "\n"
                    "date parametris ir string"
                    "company parametris ir string"
                    "name parametris ir string"
                    "quantity parameters ir float"
                    "price parameters ir float"
                    "typeid ir integer"
                    "correctQuantity ir float"
                    "\n"
                ])
            outputJson = result.text.replace("json", "").replace("`", "").replace("\t", "").replace("\n", "")
            print(outputJson)
            output = json.loads(outputJson, object_hook=lambda d: SimpleNamespace(**d))
            for itemInOutput in output:
                print()
                print(list_of_dicts)
                print(itemInOutput)
                print()
                itemEmissionByUnit = [item for item in list_of_dicts if item['type_id'] == itemInOutput.typeid][0]['value']
                print(itemEmissionByUnit)
                itemEmission = itemEmissionByUnit * itemInOutput.correctQuantity
                all_data.append((
                                itemInOutput.company,
                                itemInOutput.date,
                                itemInOutput.name,
                                itemInOutput.quantity,
                                itemInOutput.price,
                                itemEmission,
                                filename
                            ))

    if all_data:
        save_to_db(all_data)

    return render_template('index.html', message="Dati veiksmīgi saglabāti!", extracted_data=all_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        try:
            save_user(username, generate_password_hash(password))
            flash('Registration successful!', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Username already exists!', 'error')

    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    bundles = []
    bundles.append(("first","second","third"))
    bundles.append(("fourth","fifth","sixth"))

    return render_template('profile.html', bundles = bundles)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = find_user(username)

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            flash('Login successful!', 'success')
            return redirect('/')
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')

@app.route('/export', methods=['GET'])
def export_to_excel():
    if 'user_id' not in session:
        return redirect('/login')
    try:
        # Убедитесь, что папка для скачивания существует
        if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
            os.makedirs(app.config['DOWNLOAD_FOLDER'])

        # Считывание данных из базы данных
        with sqlite3.connect(DATABASE) as conn:
            df = pd.read_sql_query("SELECT * FROM invoices", conn)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Invoices')

            workbook = writer.book
            worksheet = writer.sheets['Invoices']

            # Identify the column with values to sum (e.g., 'amount')
            total_column = 'emisija'
            if total_column in df.columns:
                # Get the column index (0-based) for the 'amount' column
                col_idx = df.columns.get_loc(total_column)
                # Calculate the range for summation
                start_row = 1  # Row 1 in Excel corresponds to DataFrame index 0
                end_row = len(df)  # Length of the DataFrame
                total_row = end_row + 1  # Total row comes after the last data row

                formula = f"=SUM({chr(65 + col_idx)}{start_row + 1}:{chr(65 + col_idx)}{end_row + 1})"
                worksheet.write(total_row, col_idx, formula, workbook.add_format({'bold': True}))
                worksheet.write(total_row, col_idx - 1, "Total", workbook.add_format({'bold': True}))


        output.seek(0)
        today = datetime.today().strftime('%d/%m/%Y').replace("/","-")
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='exported_invoices_'+today  + '.xlsx'
        )

    except Exception as e:
        return render_template("index.html", message="Kļūda, mēģiniet vēlreiz!", show_popup="True")

if __name__ == '__main__':
    # Инициализация базы данных
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(debug=True)
