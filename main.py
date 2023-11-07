import threading
import time
import tkinter as tk
from CustomScrollBar import ScrollBar
from shared import *
from Step import Step
import cv2
from PIL import Image, ImageTk

app = tk.Tk()
app.title("Project Pete")

# "responsive" sizing
min_width = int(app.winfo_screenwidth() * 0.85)
min_height = int(app.winfo_screenheight() * 0.7)
app.minsize(width=min_width, height=min_height)

# Create a frame for the live stream
left_frame = tk.Frame(app, bg=dark_theme_background, width=0.7 * min_width)
left_frame.pack(side="left", fill="both", expand=False)

# Create a label to display stream
livestream = tk.Label(left_frame, )
livestream.pack(padx=(80, 50), pady=(40, 0))

# Retrieving live stream
def update_frame():
    # cap = cv2.VideoCapture(live_stream_url)
    cap = cv2.VideoCapture(0)  # camera
    if cap.isOpened():
        while True:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (750, 450))
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                livestream.config(image=photo)
                livestream.image = photo
    cap.release()


# Separate thread for live stream to not cause lagging
update_thread = threading.Thread(target=update_frame)
update_thread.daemon = True
update_thread.start()

# Logs
lw = int(left_frame.winfo_screenwidth() * 0.5)

# Performance
performance = tk.Frame(left_frame, bg=dark_theme_background, width=lw)
performance.pack(side="left", fill="both", expand=False)
performance_header = tk.Label(performance, text="Performance", bg=dark_theme_background, font=("Arial", 24, 'bold'))
performance_header.pack(padx=(80, 0), pady=(10, 0))

# Create a label to display the runtime
runtime_label = tk.Label(performance, bg=dark_theme_background, text="Runtime: 0 seconds")
runtime_label.pack(padx=(100, 0))


# Function to update the runtime label
def update_runtime():
    start_time = time.time()
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        # Format elapsed time into hh:mm:ss
        hours, remainder = divmod(int(elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)

        runtime_str = f"Runtime: {hours:02d}:{minutes:02d}:{seconds:02d}"
        runtime_label.config(text=runtime_str)

        time.sleep(1)  # Update the label every 1 second


# Create a thread for updating the runtime label
runtime_thread = threading.Thread(target=update_runtime)
runtime_thread.daemon = True
runtime_thread.start()

# Data
data = tk.Frame(left_frame, width=lw, bg=dark_theme_background)
data.pack(side="left", fill="both", expand=True)
data_header = tk.Label(data, text="Data", bg=dark_theme_background, anchor='w',
                       justify="left", font=("Arial", 24, 'bold'))
data_header.pack(pady=(10, 0))

# =====================================================================================

# Create a frame for the steps list (30%)
right_frame = tk.Frame(app, width=0.3 * min_width, bg=dark_theme_background)
right_frame.pack(side="right", fill="both", expand=True)

# Scrollable list view
canvas = tk.Canvas(right_frame, bg=dark_theme_background, borderwidth=0, highlightthickness=0)
procedure_list = tk.Frame(canvas, bg=dark_theme_background, borderwidth=0, highlightthickness=0)
scrollbar = ScrollBar(procedure_list, orient="vertical", command=canvas.yview)
procedure_list.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="top", fill="both", expand=True, pady=(40, 0))
scrollbar.pack(side="left", fill="y", expand=False)
procedure_list.pack(side="right", fill="both", expand=True)
canvas.create_window((0, 0), window=procedure_list, anchor="nw", tags="canvas_frame")

# Add dummy steps to the procedure
procedure = []
current_step = 0
for i in range(10):
    if i < 2:
        t = i
    elif i == 2:
        t = 2
    else:
        t = 3
    s = Step(index=i + 1, title=f"Step  {i + 1}", description="[wrench type], [other relevant info]",
             status=list(colors.keys())[t])
    procedure.append(s)

# initialize lists in GUI
for step in procedure:
    if step.status == IN_PROGRESS: current_step = step.index
    step.build(procedure_list)


# override button
def override_mark_done(e):
    global current_step
    # print("hay")
    isLastStep = current_step == len(procedure)
    procedure[current_step - 1].update_status(DONE_OV, isFocus=isLastStep)

    canvas.yview_moveto(1.0)
    if isLastStep: return

    current_step += 1
    procedure[current_step - 1].update_status(IN_PROGRESS)


override = tk.Label(right_frame, fg='white', bg=override_button_color, text="Override - mark done", borderwidth=5)
override.pack(fill="x", expand=False, padx=(10, 25), pady=(20, 10))
override.bind("<ButtonRelease-1>", override_mark_done)

app.mainloop()
