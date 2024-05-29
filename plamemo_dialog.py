import tkinter as tk
from tkinter import filedialog
import re
import pyglet
import os

pyglet.font.add_file('Seibi-Ai-B_Regular.otf')

dialog = []
current = 0

nama_file = ""

def import_file():
    global nama_file
    file_path = filedialog.askopenfilename(title="Pilih File Scenario (txt)", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    nama_file = os.path.basename(file_path)
    label_file.config(text=nama_file)
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            global dialog
            global current
            dialog = []
            dialog = file.readlines()
            current = 0
            update_text(current)
            file.close()

def export_file():
    if not os.path.exists("dump"):
        os.mkdir("dump")     
   
    with open("dump/"+nama_file, "w", encoding='utf-8') as file:
        for line in dialog:
            line = line.replace("\n", "\\n")
            file.write(line[:-2]+"\n")
        file.close()
   

def update_text(index):
    global dialog
    global root
    line = dialog[index]

    name = re.findall(r'\<(.*?)\>', line)
    result = re.sub(r'\<(.*?)\>', "" , line)
    result = result.replace("\\n","\n")

    text.delete('1.0', tk.END)
    text.insert(tk.END, result)

    if len(name) > 0:
        label_nama.config(text=name[0])
    else:
        label_nama.config(text="<...>")

    label_posisi.config(text=f"{current+1}/{len(dialog)}")

def next_dialog():
    global current
    global dialog
    current += 1
    if current > len(dialog)-1:
        current = 0
    update_text(current)

def prev_dialog():
    global current
    global dialog
    current -= 1
    if (current < 0):
        current = len(dialog)-1
    update_text(current)

def save_dialog(event):
    global dialog
    global current
    result = ""

    nama = label_nama.cget("text")
    if nama != "<...>":
        result = "<" + nama + ">" + text.get("1.0", tk.END)
    else:
        result = text.get("1.0", tk.END)
    result = re.split(r'[\n\r]+', result)

    dialog[current] = "\n".join(result)

def jump_dialog(event):
    global current
    global dialog
    current = int(jump.get())-1
    if current > len(dialog)-1:
        current = 0
    update_text(current)
    jump.delete(0, tk.END)


root = tk.Tk()
root.title("Plamemo Dialog")
root.geometry("730x275")
root.resizable(width=False, height=False)

# Import Export Frame
topFrame = tk.Frame(root)
topFrame.pack(side=tk.TOP)

import_button = tk.Button(topFrame, text="Import File", command=import_file)
import_button.pack(side=tk.LEFT)

export_button = tk.Button(topFrame, text="Export File", command=export_file)
export_button.pack(side=tk.RIGHT)

# Navigation Frame
navFrame = tk.Frame(root)
navFrame.pack(side=tk.TOP)

next_button = tk.Button(navFrame, text=">>", command=next_dialog)
next_button.pack(side=tk.RIGHT)

prev_button = tk.Button(navFrame, text="<<", command=prev_dialog)
prev_button.pack(side=tk.LEFT)

# Dialog Frame
dialogFrame = tk.Frame(root, pady=10)
dialogFrame.pack(side=tk.TOP, fill=tk.X)

nameFrame = tk.Frame(dialogFrame)
nameFrame.pack(side=tk.TOP, fill=tk.X)

label_nama = tk.Label(nameFrame, text="<...>", font=("Helvetica", 24))
label_nama.pack(side=tk.LEFT)

text = tk.Text(dialogFrame, height = 3, font=("Seibi-Ai-B_Regular", 22))
text.pack(side=tk.TOP)
text.bind('<KeyRelease>', save_dialog)

bottomFrame = tk.Frame(root)
bottomFrame.pack(side=tk.TOP, fill=tk.X)

label_posisi = tk.Label(bottomFrame, text="0/0", font=("Helvetica", 21))
label_posisi.pack(side=tk.TOP)

label_file = tk.Label(bottomFrame, font=("Helvetica", 16))
label_file.pack(side=tk.RIGHT)

lompat = tk.Label(bottomFrame,text="Lompat " ,font=("Helvetica", 16))
lompat.pack(side=tk.LEFT)

jump = tk.Entry(bottomFrame, font=("Helvetica", 16), width=5)
jump.pack(side=tk.LEFT)
jump.bind('<Return>', jump_dialog)
# Run the Tkinter event loop
root.mainloop()
