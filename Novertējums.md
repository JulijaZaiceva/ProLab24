## Problēmsituācija: Rēķinu apstrāde ar OCR un datu analīze;
**Eksperimenta mērķis:** izstrādāt programmatūru, kas spēj nolasīt un definēt datus no PDF formāta failiem, un sniegt lietotājiem pieprasītus datus par CO2 emisijām, balstoties uz nolasītiem datiem;
**Ieejas parametri:**
•	PDF formāta rēķins vai vairāki rēķini ar nopirktiem produkta veidu un daudzumu;
•	Produktu iespējamie veidi (produktu grupas) un tam noteikts vidējais CO2 emisiju daudzums uz vienu vienību.
**Novērtēšanas mēri:**
•	Rēķinu skaits, kuras tiek apstrādātas vienlaicīgi;
•	Rēķinu skaits, kur precīzi nolasīts produkta nosaukumu un produkta daudzums;
•	Pareiza vai iespējami pareizas produktu veidu grupā piešķiršana;
•	Precīzi sagatavotu pārskatu ar aprēķiniem skaits.
**Eksperimentu plāns:**
1. Litotājs izveido savu profilu, izmantojot loginu un paroli;
2. Lietotājs ienāk savā profilā. Ja lietoājs ir tikko reģistrējis, viņam nebūs iepriekšējo ielādēto rēķinu, savukārt jau esošajam lietotājam būs iespēja apskatīt iepriekšejo rēķinu datus
3. Lietotājs ielādē (pievieno) rēķinu vai vairākus rēķinus, lai saņemtu aprēķināto CO2;
4. Notiek laika skaitīšana, kamēr algoritms lasa datus;
5. Lietotājam ir parādīti dati: rēķina izveidotājs (firma), rēķina datums, produkts, daudzums, cena un emisiju daudzums uz produkta daudzumu
6. Lietotājs var eksportēt .xslx formāta failu ar aprēķinātiem datiem. Failā būs norādīts saraksts ar produktiem un emisiju daudzums par katru, kā arī būs norādīta kopēja emisiju summa
