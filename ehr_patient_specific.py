import tkinter as tk
import csv
import openai

openai.api_key = "sk-XXX"

def read_csv_file(file_name):
    data = []
    with open(file_name, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def construct_patient_dictionary(subject_id, csv_files):
    patient_info = {}
    for file in csv_files:
        data = read_csv_file(file)
        print(f"Columns in {file}: {', '.join(data[0].keys())}")
        for row in data:
            try:
                if row['subject_id'] == subject_id:
                    patient_info.update(row)
            except:
                print(file + " does not have a subject_id col")
    return patient_info

def query_patient_info(patient_info, query):
    # Convert patient_info to a text string
    patient_text = '\n'.join([f"{key}: {value}" for key, value in patient_info.items()])

    # Combine the patient_text and the query
    prompt = f"Patient Information:\n{patient_text}\nQuery: {query}\n"

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )

    return response.choices[0].text.strip()

def submit_query():
    subject_id = subject_id_entry.get()
    query = query_text.get("1.0", tk.END).strip()

    patient_info = construct_patient_dictionary(subject_id, csv_files)
    print(patient_info)
    response = query_patient_info(patient_info, query)
    response_text.delete("1.0", tk.END)
    response_text.insert(tk.END, response)

# Define which CSV files to browse here
csv_files = [
    'ADMISSIONS.csv',
    'CALLOUT.csv',
    'CHARTEVENTS.csv',
    'CPTEVENTS.csv',
    'DATETIMEEVENTS.csv',
    'DIAGNOSES_ICD.csv',
    'DRGCODES.csv',
    'ICUSTAYS.csv',
    'INPUTEVENTS_CV.csv',
    'INPUTEVENTS_MV.csv',
    'LABEVENTS.csv',
    'MICROBIOLOGYEVENTS.csv',
    'OUTPUTEVENTS.csv',
    'PATIENTS.csv',
    'PRESCRIPTIONS.csv',
    'PROCEDUREEVENTS_MV.csv',
    'PROCEDURES_ICD.csv',
    'SERVICES.csv',
]

window = tk.Tk()
window.title("Patient Query")
window.geometry("400x300")

# Subject ID label and entry field
subject_id_label = tk.Label(window, text="Subject ID:")
subject_id_label.pack()
subject_id_entry = tk.Entry(window)
subject_id_entry.pack()

# Query label and text area
query_label = tk.Label(window, text="Query:")
query_label.pack()
query_text = tk.Text(window, height=4)
query_text.pack()

# Submit button
submit_button = tk.Button(window, text="Submit", command=submit_query)
submit_button.pack()

# Response label and text area
response_label = tk.Label(window, text="Response:")
response_label.pack()
response_text = tk.Text(window, height=9)
response_text.pack()

# Start main window
window.mainloop()
