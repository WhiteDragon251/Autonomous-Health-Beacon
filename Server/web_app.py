from time import time
from pywebio import start_server
from pywebio.input import input_group
from pywebio.input import input as web_input
from pywebio.output import clear, put_buttons, put_markdown, put_table
import sqlite3


go_back = 0
def program():
  clear()
  put_markdown("# Vital Sign Viewer")
  put_markdown('### Choose an option')
  put_buttons(['View Vital Signs','Register a patient'], onclick=options)

def options(button):
  if button == 'View Vital Signs':
    patient_list(button)
  elif button == 'Register a patient':
    register()
  elif button == 'Go Back':
    program()
  

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
  
  connection_db = sqlite3.connect('vital_signs.db')
  mydb = connection_db.cursor()
  mydb.execute('select * from patients where name=?',(name,))
  result = mydb.fetchall()
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

      clear()
      put_markdown("# Vital Sign Viewer")
      put_markdown("### The details of the Patient are given below")
      put_markdown(f"**Name of the patient:** {name}")
      put_table(table)

      put_buttons(['Go Back'],onclick=check_to_go_back)
      refresh = 0
      
    elif int(time()) == (start + 10):
      refresh = 1
      start = int(time())
    elif go_back == 1:
      go_back = 0
      break
  program()
    

def check_to_go_back(button):
  global go_back
  if button == 'Go Back':
    go_back = 1


if __name__ == "__main__":
  start_server(program, port=1025)
