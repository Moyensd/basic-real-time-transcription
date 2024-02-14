import customtkinter as ctk
import speech_recognition as sr
import threading


# ... Placeholder imports for speech-to-text engine (comment out for now)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

recognizer = sr.Recognizer()
root = ctk.CTk()
root.geometry("600x400")

# Language selection
language_label = ctk.CTkLabel(master=root, text="Language:")
language_label.pack()
language_dropdown = ctk.CTkComboBox(master=root, values=["English", "Japanese", "Chinese"])
language_dropdown.pack()

# Audio Source selection
audio_source_label = ctk.CTkLabel(master=root, text="Audio Source:")
audio_source_label.pack()

# Get available audio input devices
audio_devices = sr.Microphone.list_microphone_names()
audio_source_dropdown = ctk.CTkComboBox(master=root, values=audio_devices)
audio_source_dropdown.pack()

microphone_dict = {}
for index, name in enumerate(sr.Microphone.list_microphone_names()):
        microphone_dict[name] = index

# Transcription display
transcript_frame = ctk.CTkFrame(master=root)
transcript_frame.pack(pady=20, padx=10, fill="both", expand=True)
transcript_text = ctk.CTkTextbox(master=transcript_frame)  # Set wraplength to the desired width
transcript_text.pack(expand=True, fill="both")
transcript_text.configure(state="disabled")

# Flags and events
is_transcribing = threading.Event()
stop_event = threading.Event()

def toggle_transcription():
    global is_transcribing
    if is_transcribing.is_set():
        stop_transcription()

    else:
        start_transcription()
        # Update button text immediately
        update_button_text()

def start_transcription():
    is_transcribing.set()

def stop_transcription():
    is_transcribing.clear()
    stop_event.set()

def transcribe_thread():
    while True:
        if is_transcribing.is_set():
            selected_name = str(audio_source_dropdown.get())
            selected_index = microphone_dict[selected_name]
            with sr.Microphone(device_index=selected_index) as source:
                print("Say something...")
                audio = recognizer.listen(source)

            try:
                language_code = {"English": "en-US", "Japanese": "ja", "Chinese": "zh-CN"}[language_dropdown.get()]
                transcript_text.configure(state="normal")
                text = recognizer.recognize_google(audio, language=language_code)

                # Insert the new text
                transcript_text.insert("end", text + "\n")

                transcript_text.configure(state="disabled")
                print("text scribed")

            except sr.UnknownValueError:
                transcript_text.configure(state="normal")
                transcript_text.insert("end", "Could not understand audio\n")
                transcript_text.configure(state="disabled")
            except sr.RequestError as e:
                transcript_text.configure(state="normal")
                transcript_text.insert("end", f"Error with the transcription service; {e}\n")
                transcript_text.configure(state="disabled")
            finally:
                stop_event.wait(timeout=0.8)  
                stop_event.clear()  # Clear stop event after waiting

def update_button_text():
    if is_transcribing.is_set():
        toggle_button.configure(text="Stop Transcription")
    else:
        toggle_button.configure(text="Start Transcription")



# Toggle button
toggle_button = ctk.CTkButton(master=root, text="Start Transcription", command=toggle_transcription)
toggle_button.pack(pady=10)  # Add this line to display the button

# Status label (optional)
# status_label = ctk.CTkLabel(master=root, text="")
# status_label.pack()

# Run transcription thread in the background
transcription_thread = threading.Thread(target=transcribe_thread)
transcription_thread.start()

root.mainloop()
