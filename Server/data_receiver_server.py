from queue import Empty
import socketserver
import sqlite3


connection = sqlite3.connect('vital_signs.db')
mydb = connection.cursor()
class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("Receiving Data...")
        self.data = self.request.recv(1024).strip()
        # print("{} wrote:".format(self.client_address[0]))
        recv = self.data.decode('UTF-8')
        recv = tuple(recv.split('-'))

        # Checking if patient is present
        mydb.execute('select * from patients where id=?',(recv[0],))
        result = mydb.fetchall()
        if len(result) == 1:
            mydb.execute("INSERT OR IGNORE INTO readings (id, bp, pulse, temp, breath) VALUES (?, ?, ?, ?, ?)", recv)
            connection.commit()

            # Format: <id>-<bp>-<pulse>-<temp>-<rp>

            print("Data written to table readings")
            mydb.execute('select * from readings')
            result = mydb.fetchall()
            print(result)
        else:
            print('Patient is not present in the database')

if __name__ == "__main__":
    HOST, PORT = "192.168.0.35", 9999

    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
