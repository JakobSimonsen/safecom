import PySimpleGUI as sg
import json
import coordinator_stm

with open('./channels.json') as f:
    channel_values = json.load(f)

title_font = ('Arial', 25)
normal_font = ('Arial', 18)
sg.theme('DarkBlue4')
default_channel = channel_values['channel1']

msg = coordinator_stm.client.GetHistory()

title = [sg.Text('This is your new awesome walkie talkie', font=title_font)]


messages = [sg.Listbox(values=msg,
                       size=(30, 6), font=normal_font, enable_events=True, key='message')]

channels = sg.Combo([channel_values[v]['name'] for v in channel_values], default_value=default_channel['name'],
                    enable_events=True, key='channels', size=(15, 1), font=normal_font)
channel_button = sg.Button('Update', size=(
    10, 1), key='Update', font=normal_font)

priority = [sg.Checkbox('Priority', key="Priority", font=normal_font)]
record_button = [sg.Button('Record', size=(
    25, 1), key='Record', visible=True, font=normal_font)]
stop_button = [sg.Button('Stop and Send', size=(25, 1),
                         key='Stop', visible=False, font=normal_font)]

# All the stuff inside your window.
layout = [title,
          messages,
          [channels, channel_button],
          priority,
          record_button,
          stop_button]

margins = (100, 50)

coordinator_stm.driver.send(
    "change_channel", "coordinator", args=[default_channel['topic']])

# Create the Window
window = sg.Window('Walkie Talkie boj', layout, margins,
                   text_justification="center", element_justification="center")


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read(timeout=10)
    if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
        break

    elif event == 'Record':
        print('recording')
        coordinator_stm.driver.send("record_button", "coordinator")
        window['Record'].Update(visible=False)
        window['Stop'].Update(visible=True)

    elif event == 'Stop':
        print('stop recording')
        coordinator_stm.driver.send(
            "end_recording_button", "coordinator", args=[values['Priority']])
        window['Record'].Update(visible=True)
        window['Stop'].Update(visible=False)

    elif event == 'Update':
        channel_name = values['channels']
        for channel in channel_values.values():
            if channel['name'] == channel_name:
                coordinator_stm.driver.send(
                    "change_channel", "coordinator", args=[channel['topic']])

    elif event == 'message':
        message_file = values['message']
        print('Play message: ', message_file)
        coordinator_stm.driver.send(
            'play_from_history', 'coordinator', args=[message_file[0]])

    window['message'].Update(values=coordinator_stm.client.GetHistory())

coordinator_stm.driver.stop()
window.close()
