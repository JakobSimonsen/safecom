import PySimpleGUI as sg

# All the stuff inside your window.
layout = [[sg.Text('This is your new awesome walkie talki')],
          [sg.Listbox(values=["Message 1", "Message2"], size=(30, 10))],
          [sg.Button('Ok'), sg.Button('Cancel')]]
margins = (100, 50)
# Create the Window
window = sg.Window('Walkie Talkie boj', layout, margins)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break

window.close()
