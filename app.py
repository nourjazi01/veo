from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import csv

app = Flask(__name__)

PRODUCT_TYPES = {
    "bien_etre_de_la_personne": "bien_etre_de_la_personne",
    "boissons": "boissons",
    "DPH": "DPH",
    "epiceries": "epiceries",
    "equipement_de_la_maison": "equipement_de_la_maison",
    "habillement": "habillement",
    "produits_frais": "produits_frais",
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        country = request.form.get('country')
        department = request.form.get('department')
        product = request.form.get('product')
        return redirect(url_for('results', country=country, department=department, product=product))
    return render_template('index.html')

@app.route('/check-crm', methods=['GET'])
def check_crm():
    siren = request.args.get('siren')
    if not siren:
        return jsonify({"error": "SIREN number is required"}), 400

    file_path = "datasets/crm.csv"
    
    try:
        if not os.path.exists(file_path):
            return jsonify({"error": "CRM dataset not found"}), 404

        with open(file_path, 'r', encoding='utf-8-sig') as file:  # Note the encoding
            # Read all lines and clean them
            lines = [line.strip() for line in file.readlines()]
            if not lines:
                return jsonify({"error": "Empty CRM file"}), 500

            # Get headers and clean them
            headers = [h.strip().upper() for h in lines[0].split(',')]
            
            # Find SIREN column
            try:
                siren_index = headers.index('SIREN')
            except ValueError:
                return jsonify({"error": "SIREN column not found"}), 500

            # Check each line
            for line in lines[1:]:  # Skip header
                if not line.strip():  # Skip empty lines
                    continue
                    
                values = [v.strip() for v in line.split(',')]
                if len(values) > siren_index:
                    if values[siren_index] == siren:
                        return jsonify({"exists": True})

        return jsonify({"exists": False})

    except Exception as e:
        print(f"Error checking CRM: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/results')
def results():
    country = request.args.get('country')
    department = request.args.get('department', '').strip()
    product = request.args.get('product')

    print(f"Searching for - Country: {country}, Department: {department}, Product: {product}")

    file_path = f"datasets/{product}.csv"
    if not os.path.exists(file_path):
        return render_template('results.html', error=f"Dataset not found: {file_path}")

    suppliers = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            search_dept = department.zfill(2)
            
            for row in csv_reader:
                row_dept = str(row.get("departement", "")).strip().zfill(2)
                row_country = row.get("pays", "").strip()

                print(f"Comparing - Row: {row_country}/{row_dept} with Search: {country}/{search_dept}")

                if (row_country.lower() == country.lower() and 
                    row_dept == search_dept):
                    suppliers.append(row)
                    print(f"Match found: {row}")

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return render_template('results.html', error=f"Error reading dataset: {str(e)}")

    print(f"Total suppliers found: {len(suppliers)}")
    return render_template('results.html', 
                         suppliers=suppliers, 
                         country=country, 
                         department=department, 
                         product=product)

if __name__ == '__main__':
    app.run(debug=True)