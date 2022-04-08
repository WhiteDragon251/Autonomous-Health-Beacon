import socketserver
import sqlite3
from socket import gethostname, gethostbyname


connection = sqlite3.connect('vital_signs.db')
mydb = connection.cursor()
class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        recv = self.data.decode('UTF-8')
        recv = tuple(recv.split('-'))

        # Checking if patient is present
        mydb.execute('select * from patients where id=?',(recv[0],))
        result = mydb.fetchall()
        if len(result) == 1:
            # Format: <id>-<bp>-<pulse>-<temp>-<rp>
            mydb.execute("INSERT OR IGNORE INTO readings (id, pulse, temp, breath) VALUES (?, ?, ?, ?)", recv)
            connection.commit()

            print("Data written to table readings")
            print('-'*20)
        # else:
            # print('Patient is not present in the database')

if __name__ == "__main__":
    HOST, PORT = gethostbyname(gethostname()), 9999

    print(f'Server is running at {HOST} on port {PORT}')
    print("Receiving Data...")
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
