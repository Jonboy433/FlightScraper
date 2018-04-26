'''from tkinter import *
from tkinter.ttk import Frame, Button, Entry, Label, OptionMenu

root = Tk()

# Create widgets
frame = Frame(root, borderwidth=5)
searchFrame = Frame(frame, borderwidth=7)
optionsFrame = Frame(frame, borderwidth=7)
resultsFrame = Frame(frame, borderwidth=7)
label_from_airport = Label(searchFrame, background='cyan', width=10, text='From:')
label_to_airport = Label(searchFrame, background='cyan', width=10, text='To:')
label_depart = Label(searchFrame, background='cyan', width=10, text='Depart: ')
label_return = Label(searchFrame, background='cyan', width=10, text='Return: ')
fromAirport = StringVar()
toAirport = StringVar()
entry_from_airport = Entry(searchFrame, width=5, textvariable=fromAirport)
entry_to_airport = Entry(searchFrame, width=5, textvariable=toAirport)
departDate = StringVar()
returnDate = StringVar()
entry_depart_date = Entry(searchFrame, width=7, textvariable=departDate)
entry_return_date = Entry(searchFrame, width=7, textvariable=returnDate)
btn_ok = Button(searchFrame, text='Search')
text_results = Text(resultsFrame)

btn_test = Button(optionsFrame, text='Test')

# Grid management
frame.grid(column=0, row=0)
searchFrame.grid(column=0, row=0, sticky=W)
optionsFrame.grid(column=1, row=0, sticky=W)
resultsFrame.grid(column=0, row=1, columnspan=2, sticky=EW)
label_from_airport.grid(column=0, row=0, sticky=E)
entry_from_airport.grid(column=1, row=0, ipadx=4, sticky=W)
label_to_airport.grid(column=0, row=1, sticky=E)
entry_to_airport.grid(column=1, row=1, ipadx=4, sticky=W)
label_depart.grid(column=0, row=2, sticky=E)
entry_depart_date.grid(column=1, row=2, ipadx=4, sticky=W)
label_return.grid(column=0, row=3, sticky=E)
entry_return_date.grid(column=1, row=3, ipadx=4, sticky=W)
btn_ok.grid(column=0, row=4, sticky=E)
text_results.grid(column=0, row=0)


btn_test.grid(column=0, row=0, sticky=W)


root.mainloop()'''

import sys
from PyQt5 import QD

class App(QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'FlightScraper'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 100
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        label_from_airport

        self.show()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())