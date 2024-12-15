import pandas as pd

def organize_excel_attendance(input_file, output_file):
    # Leer el archivo de Excel
    data = pd.read_excel(input_file)

    # Filtrar las columnas necesarias
    filtered_data = data[['UID', 'Name', 'DateTime']].copy()

    # Convertir la columna DateTime a formato datetime
    filtered_data['DateTime'] = pd.to_datetime(filtered_data['DateTime'], errors='coerce')

    # Eliminar filas con valores no válidos en DateTime
    filtered_data = filtered_data.dropna(subset=['DateTime'])

    # Extraer el día de la semana y la fecha
    filtered_data['Day'] = filtered_data['DateTime'].dt.day_name()
    filtered_data['Date'] = filtered_data['DateTime'].dt.date

    # Agrupar y reestructurar los datos
    pivoted_data = filtered_data.groupby(['UID', 'Name', 'Day', 'Date'])['DateTime'].apply(
        lambda x: '\n'.join(x.dt.strftime('%H:%M:%S'))
    ).reset_index()

    # Crear columnas por días de la semana con sus fechas
    reshaped_data = pivoted_data.pivot(index=['UID', 'Name'], columns=['Day', 'Date'], values='DateTime')

    # Aplanar las columnas multiíndice y ordenar los días
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    reshaped_data.columns = [f"{day} {date}" for day, date in reshaped_data.columns]
    reshaped_data = reshaped_data.reindex(
        columns=sorted(reshaped_data.columns, key=lambda x: (days_order.index(x.split()[0]), x))
    )

    # Completar con "Descanso" los días sin registros
    reshaped_data = reshaped_data.fillna("Descanso")

    # Resetear el índice para obtener una tabla limpia
    reshaped_data.reset_index(inplace=True)

    # Guardar los resultados en un archivo Excel
    reshaped_data.to_excel(output_file, index=False)

    print(f"Archivo procesado y guardado en {output_file}")

# Ejecución del programa
input_file = 'datos filtrados.xlsx'  # Reemplaza con la ruta real del archivo de entrada
output_file = 'finales.xlsx'  # Reemplaza con la ruta real del archivo de salida
organize_excel_attendance(input_file, output_file)
