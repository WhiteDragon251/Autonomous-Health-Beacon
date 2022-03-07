from multiprocessing import connection
from time import time
from pywebio import start_server
from pywebio.input import input_group
from pywebio.input import input as web_input
from pywebio.output import clear, put_buttons, put_markdown, put_table
import sqlite3


connection_db = sqlite3.connect('vital_signs.db')
mydb = connection_db.cursor()

go_back = 0
def program():
  clear()
  put_markdown("# Vital Sign Viewer")
  put_markdown('### Choose an option')
  put_buttons(['View Vital Signs','Register a patient'], onclick=options)

def options(button):
  if button == 'View Vital Signs':
    # vital_signs(button)
    patient_list(button)
  elif button == 'Register a patient':
    register()
  elif button == 'Go Back':
    program()
  
# def add_patient_in_db(patient_dictionary):

def register():
  clear()
  put_markdown("# Vital Sign Viewer")
  put_markdown("### Register")
  patient_details = input_group('Please fill up the details below', [
    web_input('Name', name='name'), 
    web_input('Blood Pressure Monitoring Value', name='bp'),
    web_input('Pulse Rate Monitoring Value', name='pulse'),
    web_input('Temparture Monitoring Value', name='temp'),
    web_input('Respiration Rate Monitoring Value', name='rp'),
  ])

  default_values = {'bp':120,'pulse':70,'temp':100,'rp':90} # Default values for vital signs
  if patient_details['name'] != '':

    for key in patient_details:
      if patient_details[key] == '':
        patient_details[key] = default_values[key]

    # print(patient_details)
    # with open('patients.txt', 'a') as patients:
      # patients.write('\n' + str(patient_details))

    # with open('patients_name.txt', 'a') as patients_names:
      # patients_names.write('\n' + str(patient_details['name']))
    
    connection_db = sqlite3.connect('vital_signs.db')
    mydb = connection_db.cursor()
    mydb.execute('select max(id) from patients')
    max_id = int(mydb.fetchone()[0])
    patient_details['id'] = max_id + 1

    mydb.execute('insert into patients values (:id, :name, :bp, :pulse, :temp, :rp)', patient_details)
    connection_db.commit()
    put_markdown('Your response has been recorded successfully')
    connection_db.close()

  else:
    put_markdown("Your response wasn't recorded as no name was entered for the patient")

  put_buttons(['Go Back'], onclick=options)


def patient_list(button):
  clear()
  global recv_id
  put_markdown("# Vital Sign Viewer")
  name = web_input('Enter the name of the patient whose details you want to view')
  # with open('patients_name.txt', 'r') as patient_names:
    # names = [ x.strip('\n') for x in patient_names.readlines()]
  
  connection_db = sqlite3.connect('vital_signs.db')
  mydb = connection_db.cursor()
  mydb.execute('select * from patients where name=?',(name,))
  result = mydb.fetchall()
  # print(result)
  connection_db.close()
  
  if len(name) != 0 :
    recv_id = result[0][0]
    vital_signs(recv_id)
  else:
    put_markdown("The name entered was not found in the list of patients registered")
    put_buttons(['Go Back'], onclick=options)

def vital_signs(button):
  global recv_id
  global go_back
  start = int(time())
  refresh = 1
  while True:
    if refresh == 1:
      # Getting readings data
      table = [
        ['Time', 'Blood pressure', 'Pulse Rate', 'Temperature', 'Breathing Rate']
      ]
      connection_db = sqlite3.connect('vital_signs.db')
      mydb = connection_db.cursor()
      mydb.execute('select time, bp, pulse, temp, breath from readings where id=? order by time DESC limit 5', (recv_id,))
      result = mydb.fetchall()
      mydb.execute('select name from patients where id=?', (recv_id,))
      name = mydb.fetchone()[0]
      connection_db.close()

      result = [ list(x) for x in result]
      table.extend(result)
      # print(table)

      clear()
      put_markdown("# Vital Sign Viewer")
      put_markdown("### The details of the Patient are given below")
      put_markdown(f"**Name of the patient:** {name}")
      # Bring data from database and add in 'table'
      put_table(table)
      # recv_bp = 'blank'
      # recv_pulse = 'blank'
      # recv_temp = 'blank'
      # recv_rp = 'blank' # Respiration rate

      # put_markdown(f"* **Name:** {recv_id}\n* **Blood pressure:** {recv_bp}\n* **Pulse rate:** {recv_pulse}\n* **Temperature:** {recv_temp}\n* **Respiration rate:** {recv_rp}")

      put_buttons(['Go Back'],onclick=check_to_go_back)
      refresh = 0
      # print(f'Refresh: {refresh}')

    elif int(time()) == (start + 10):
      refresh = 1
      start = int(time())
    elif go_back == 1:
      go_back = 0
      # print('Go Back was pressed')
      break
  program()
    

def check_to_go_back(button):
  global go_back
  if button == 'Go Back':
    go_back = 1


if __name__ == "__main__":
  start_server(program, port=1025)