import tkinter as tk
import csv
import openai
import string
import random


openai.api_key = "sk-XXX"
 # Replace with your own OpenAI key. 

def load_csv(file_path):
    records = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(row)
    return records

def build_patient_data(subject_id, csv_files, field_two, value_two):
    patient_info = {}
    for file in csv_files:
        data = load_csv(file)
        for row in data:
            try:
                if row['subject_id'] == subject_id and row[field_two.strip().lower()].lower() == value_two.lower():
                    patient_info.update(row)
            except KeyError:
                continue
    return patient_info

def query_patient_data(patient_data, query_text):
    patient_info_str = '\n'.join([f"{key}: {value}" for key, value in patient_data.items()])
    prompt = f"Patient Information:\n{patient_info_str}\nQuery: {query_text}\n"

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )

    return response.choices[0].text.strip()

def find_matching_subject_ids(csv_files, field_two, value_two):
    matching_ids = []
    for csv_file in csv_files:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for record in reader:
                if field_two.strip().lower() in record:
                    if value_two.lower() in record[field_two.strip().lower()].lower():
                        subject_id = record['subject_id']
                        matching_ids.append(subject_id)
    #print(matching_ids)
    return matching_ids

def list_all_fields(csv_files):
    all_fields = set()
    for file in csv_files:
        with open(file, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            fields = reader.fieldnames
            all_fields.update(fields)
    return list(all_fields)

def extract_fields_from_query(user_query, available_fields):
    # Need to experiment with stemming or some other kind of NLP thing, here running two queries is cost-intensive.
    prompt = f"What 2 things in list ({available_fields}) exist in the query ({user_query}) Respond with commas separating."

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )

    response_text = response.choices[0].text.strip()
    extracted_fields = [item.strip() for item in response_text.split(",")]

    second_prompt = f"In one word from the query itself, what is the {extracted_fields[1]} asked about in the query: {user_query}"
    second_response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=second_prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )
    second_response_text = second_response.choices[0].text.strip()
    second_response_text = second_response_text.lower()
    second_response_text = second_response_text.translate(str.maketrans('', '', string.punctuation))

    print(extracted_fields, second_response_text)
    flipper = 0 
    # Sometimes, the extracted fields will be flipped. E.g. the question: What is the strength for drug senna?
    # may result in [drug_name_generic, prod_strength]. It will then check for prod_strength values equal to senna,
    # which obviously won't work. Therefore, we may sometimes flip these two values if necessary to continue to 
    # the right answer.

    patient_datas = []
    patient_values = []
    patient_datas_flipped = []
    patient_values_flipped = []

    
    matching_ids = find_matching_subject_ids(csv_files, extracted_fields[1], second_response_text)
    counter = 0
    for id in matching_ids:
        if counter >= 5:
            break
        x = build_patient_data(id, csv_files, extracted_fields[1], second_response_text)
        patient_datas.append(x)
        counter = counter + 1

    if len(matching_ids) == 0:
        try:
            matching_ids = find_matching_subject_ids(csv_files, extracted_fields[0], second_response_text)
            for id in matching_ids:
                if counter >= 5:
                    break
                x = build_patient_data(id, csv_files, extracted_fields[0], second_response_text)
                patient_datas_flipped.append(x)
                counter = counter + 1
            flipper = 1 # 
        except:
            return "No answer found!"

    try:
        if flipper == 0:
            for patient_data in patient_datas:
                value = patient_data[extracted_fields[0].lower()]
                patient_values.append(value)
        else:
            for patient_data in patient_datas_flipped:
                value = patient_data[extracted_fields[1].lower()]
                patient_values_flipped.append(value)
    except KeyError:
        value = "No answer found!"

    return (patient_values if flipper == 0 else patient_values_flipped)

def run_query():
    subject_id = subject_id_entry.get()
    query = query_text_box.get("1.0", tk.END).strip()

    if subject_id:  # If a specific subject_id is given -> Query only information for that subject
        patient_data = build_patient_data(subject_id, csv_files)
        response = query_patient_data(patient_data, query)
    else:  # If subject_id is blank -> Query it all!
        all_fields = list_all_fields(csv_files)
        response = extract_fields_from_query(query, all_fields)

    response_text_box.delete("1.0", tk.END)
    response_text_box.insert(tk.END, response)

# CSV files list
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
    'TRANSFERS.csv'
]

# Create the main window
main_window = tk.Tk()
main_window.title("Patient Query")
main_window.geometry("400x300")

# Subject ID label and entry field
subject_id_label = tk.Label(main_window, text="Subject ID:")
subject_id_label.pack()
subject_id_entry = tk.Entry(main_window)
subject_id_entry.pack()

# Query label and text area
query_label = tk.Label(main_window, text="Query:")
query_label.pack()
query_text_box = tk.Text(main_window, height=4)
query_text_box.pack()

# Submit button
submit_button = tk.Button(main_window, text="Submit", command=run_query)
submit_button.pack()

# Response label and text area
response_label = tk.Label(main_window, text="Response (up to 5 representative samples):")
response_label.pack()
response_text_box = tk.Text(main_window, height=9)
response_text_box.pack()

# Start the Tkinter event loop
main_window.mainloop()
