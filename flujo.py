import re
import pandas as pd
import pdfplumber

def extract_pdf_data(pdf_path):
    """
    Extrae los datos de un archivo PDF y los organiza en un DataFrame.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    # Dividir el texto en líneas
    lines = text.splitlines()

    # Inicializar lista para almacenar registros
    records = []
    current_record = {}

    for line in lines:
        # Verificar si la línea contiene una fecha y hora (nuevo registro)
        if re.match(r"\d{2}/\d{2}/\d{2} \d{2}:\d{2}", line):
            if current_record:
                records.append(current_record)
                current_record = {}

            parts = line.split()
            current_record["Fecha/Hora"] = parts[0] + " " + parts[1]
            current_record["Movimiento"] = parts[2] if len(parts) > 2 else ""

        elif "Garaje" in line or "Aparcamiento" in line:
            current_record["Garaje"] = line

        elif "Empleado" in line or "Tarjeta" in line:
            current_record["Observación"] = line

        elif re.match(r"\d+", line):
            current_record["No. serie"] = line

        elif re.match(r"[\d.]+", line):
            if "Importe" not in current_record:
                current_record["Importe"] = line
            else:
                current_record["Valor restante"] = line

    if current_record:
        records.append(current_record)

    # Crear un DataFrame con los registros
    df = pd.DataFrame(records)
    df['Hora'] = pd.to_datetime(df['Fecha/Hora'], format='%d/%m/%y %H:%M', errors='coerce').dt.hour

    # Contar carros por hora
    hourly_counts = df.groupby('Hora').size().reset_index(name='Vehículos')
    all_hours = pd.DataFrame({'Hora': range(24)})
    hourly_counts = pd.merge(all_hours, hourly_counts, on='Hora', how='left').fillna(0)
    hourly_counts['Vehículos'] = hourly_counts['Vehículos'].astype(int)
    return hourly_counts

def process_multiple_pdfs(pdf_paths, output_file):
    """
    Procesa múltiples PDFs, suma las columnas de horas y genera un archivo Excel.
    """
    all_data = {}
    total_vehicles = {}

    for label, pdf_path in pdf_paths.items():
        data = extract_pdf_data(pdf_path)
        all_data[label] = data.set_index('Hora')['Vehículos']
        total_vehicles[label] = data['Vehículos'].sum()

    # Combinar los datos de ambos PDF
    combined = pd.DataFrame(all_data).T  # Transponer para que las horas sean columnas
    combined['Total'] = combined.sum(axis=1)

    # Agregar una fila de totales por hora
    combined.loc['Total'] = combined.sum()

    # Guardar en Excel
    combined.to_excel(output_file, index=True)
    print(f"Datos procesados y guardados en {output_file}")

    # Mostrar totales por categoría
    for label, total in total_vehicles.items():
        print(f"Total de vehículos ({label}): {total}")

# Archivos PDF y salida
pdf_paths = {
    "Abonados": "ABONADOS  42.pdf",  # Reemplaza con el nombre real del PDF
    "Tickets": "SALIDA   42.pdf",    # Reemplaza con el nombre real del PDF
}
output_file = "Salidas 22.xlsx"

# Ejecutar el procesamiento
process_multiple_pdfs(pdf_paths, output_file)
