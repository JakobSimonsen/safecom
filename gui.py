import PySimpleGUI as sg
import json

with open('./channels.json') as f:
    channel_values = json.load(f)

title = [sg.Text('This is your new awesome walkie talki')]
messages = [sg.Listbox(values=["Message 1", "Message2"], size=(30, 10))]
channels = [sg.Combo([channel_values[v] for v in channel_values],
                     enable_events=True, key='channels', size=(15, 1))]

# All the stuff inside your window.
layout = [title,
          messages,
          channels,
          [sg.Button('Record', size=(25, 1))],
          [sg.Button('Send', size=(25, 1))]]

margins = (100, 50)

# Create the Window
window = sg.Window('Walkie Talkie boj', layout, margins,
                   text_justification="center", element_justification="center")

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
        break

    if event == 'Record':
        print('recording')

    if event == 'Send':
        print('sending')

window.close()
