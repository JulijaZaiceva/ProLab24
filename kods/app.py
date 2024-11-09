from flask import Flask, request, render_template
import google.generativeai as genai
import os

# Set up Flask app
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'upload'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

os.environ['mykey'] = 'AIzaSyCyx9WctsiaIlbQpLQzlfMl-UjIDgbvdJM'

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

chat_session = model.start_chat(
    history=[
    ]
)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # if 'file' not in request.files:
    #     return

    files = request.files.getlist('files')
    prices = {}

    for file in files:
        if file.filename == '':
            return
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(filepath)

            myfile = genai.upload_file(filepath)

            result = model.generate_content(
                [myfile, "\n\n",
                 "atrodi datumu, pēc tam pārbaudi katru tabulu, atrodi vai tajā ir kāds pakalpojums vai produkts(nodokļi un pvn nav produkts, tos neraksti),ja nav tad informāciju par šo tabulu neraksti, bet ja ir, tad turpini pārbaudīt vai ir specificēts daudzums šim produktam, pēc tam pārbaudi vai ir specificēta summa šim produktam.Ja kāds no šiem nav specificēts raksti null. Sniedz arī rēķina gala summu.  Atbildi dot  tikai šādā formātā bez papildus teksta, mērvienības rakstīt iekavās, nodokļus,PVN nerakstīt:  datums: , [produkts,daudzums, cena]. Rekur piemērs: datums: 2020.09.12, [piens,3(litri), 12.00(EUR)],  [koks,5(kg), 54.00(EUR)],  [Olas,3, 22.00(EUR)],[projektēšanas pakalpjumi,null, 12.00(EUR)"]
            )

            print(result.text)

            prices[str(filename)] = result.text

    if prices:
        return render_template('index.html', prices=prices)
    else:
        return render_template('index.html', message='Kaut kas nogāja greizi!')


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
