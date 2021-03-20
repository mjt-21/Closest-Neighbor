import main
import tkinter as tk

root = tk.Tk()
root.geometry("400x300")
root.resizable(0,0)

canvas1 = tk.Canvas(root, width = 400, height = 300)
canvas1.pack()

entry1 = tk.Entry (root) 
canvas1.create_window(200, 140, window=entry1)

button1 = tk.Button(text='Go', command=lambda: main.inRadius(6011, int(entry1.get())))
canvas1.create_window(200, 180, window=button1)

InputLabel = tk.Label(root, text="", font=("Courier", 15), width=42, height=5, borderwidth=2, relief="solid")

root.mainloop()

while True:
    print(entry1.cget("text"))
