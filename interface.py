import tkinter as tk
from tkinter import filedialog, messagebox
import time
from csp_algorithms import KakurasuSolver

# Global variables
n_val = 0
row_targets_val = []
col_targets_val = []
grid_buttons = {}
solver_generator = None
debug_history = []
debug_step = -1
start_time = 0


def load_file():
    global n_val, row_targets_val, col_targets_val
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not filepath:
        return

    try:
        with open(filepath, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if len(lines) != 3:
            raise ValueError("File must have exactly 3 rows.")

        n_val = int(lines[0])
        row_targets_val = [int(x) for x in lines[1].split(",")]
        col_targets_val = [int(x) for x in lines[2].split(",")]

        if len(row_targets_val) != n_val or len(col_targets_val) != n_val:
            raise ValueError(
                f"Rows 2 and 3 must have exactly {n_val} comma-separated numbers."
            )

        draw_grid(n_val, row_targets_val, col_targets_val)
        load_btn.config(text="Reset", command=reset_app)

    except Exception as e:
        messagebox.showerror(
            "Invalid File Format",
            f"Error: {str(e)}\n\n"
            "Format required:\n"
            "Row 1: Grid dimension (N)\n"
            "Row 2: N comma-separated row target sums\n"
            "Row 3: N comma-separated column target sums\n"
            "All values must be integers.",
        )


def reset_app():
    for widget in grid_frame.winfo_children():
        widget.destroy()
    for widget in controls_frame.winfo_children():
        widget.destroy()
    stats_label.config(text="")
    debug_frame.pack_forget()
    controls_frame.pack(side=tk.BOTTOM, pady=40)
    load_btn.config(text="Select .txt File", command=load_file)


def draw_grid(n, row_targets, col_targets):
    global grid_buttons
    grid_buttons = {}
    
    # Clear previous grid if exists
    for widget in grid_frame.winfo_children():
        widget.destroy()

    # Draw column weights (1 to n) at the top
    for j in range(n):
        tk.Label(grid_frame, text=str(j + 1), font=("Arial", 14, "bold")).grid(
            row=0, column=j + 1, padx=5, pady=5
        )

    # Draw row weights (1 to n) at the left
    for i in range(n):
        tk.Label(grid_frame, text=str(i + 1), font=("Arial", 14, "bold")).grid(
            row=i + 1, column=0, padx=5, pady=5
        )

    # Draw the N x N blank grid
    for i in range(n):
        for j in range(n):
            btn = tk.Button(grid_frame, width=4, height=2, bg="white", relief="raised")
            btn.grid(row=i + 1, column=j + 1, padx=1, pady=1)
            grid_buttons[(i + 1, j + 1)] = btn

    # Draw row targets at the right
    for i in range(n):
        tk.Label(
            grid_frame, text=str(row_targets[i]), font=("Arial", 14, "bold"), fg="blue"
        ).grid(row=i + 1, column=n + 1, padx=10)

    # Draw col targets at the bottom
    for j in range(n):
        tk.Label(
            grid_frame, text=str(col_targets[j]), font=("Arial", 14, "bold"), fg="blue"
        ).grid(row=n + 1, column=j + 1, pady=10)

    draw_controls()


def draw_controls():
    # Algorithm Dropdown
    tk.Label(controls_frame, text="Algorithm:", font=("Arial", 12)).grid(
        row=0, column=0, padx=10, pady=10
    )
    controls_frame.algo_var = tk.StringVar(value="Backtracking Search")
    algo_dropdown = tk.OptionMenu(
        controls_frame,
        controls_frame.algo_var,
        "Backtracking Search",
        "AC-3 Algorithm",
        command=lambda _: update_heuristic_dropdown(
            controls_frame.algo_var.get(),
            heuristic_dropdown,
            controls_frame.heuristic_var,
        ),
    )
    algo_dropdown.grid(row=0, column=1, padx=10, pady=10)

    # Heuristic Dropdown (Only for Backtracking)
    tk.Label(controls_frame, text="Heuristic:", font=("Arial", 12)).grid(
        row=0, column=2, padx=10, pady=10
    )
    controls_frame.heuristic_var = tk.StringVar(value="None")
    heuristic_dropdown = tk.OptionMenu(
        controls_frame, controls_frame.heuristic_var, "None", "MRV", "MCV", "LCV"
    )
    heuristic_dropdown.grid(row=0, column=3, padx=10, pady=10)

    # Execution Mode Dropdown
    tk.Label(controls_frame, text="Execution Mode:", font=("Arial", 12)).grid(
        row=0, column=4, padx=10, pady=10
    )
    controls_frame.mode_var = tk.StringVar(value="Solve")
    mode_dropdown = tk.OptionMenu(
        controls_frame, controls_frame.mode_var, "Solve", "Debug"
    )
    mode_dropdown.grid(row=0, column=5, padx=10, pady=10)

    # Start Button
    start_btn = tk.Button(
        controls_frame, text="Start", font=("Arial", 14, "bold"), bg="green", fg="white", command=start_solving
    )
    start_btn.grid(row=1, column=0, columnspan=6, pady=20)


def start_solving():
    global solver_generator, debug_history, debug_step, start_time
    
    algo = controls_frame.algo_var.get()
    heuristic = controls_frame.heuristic_var.get()
    mode = controls_frame.mode_var.get()
    
    solver = KakurasuSolver(n_val, row_targets_val, col_targets_val, algo, heuristic)
    solver_generator = solver.solve()
    
    if mode == "Solve":
        start_time = time.time()
        last_state = None
        for state in solver_generator:
            last_state = state
            if state[2] != "searching":
                break
        end_time = time.time()
        
        if last_state:
            update_grid(last_state[0])
            update_stats(last_state, end_time - start_time)
    else:
        # Debug mode
        debug_history = []
        debug_step = -1
        controls_frame.pack_forget()
        debug_frame.pack(side=tk.BOTTOM, pady=20)
        btn_right.config(state="normal")
        step_forward()


def step_forward():
    global debug_step
    if debug_step < len(debug_history) - 1:
        debug_step += 1
        state = debug_history[debug_step]
        update_grid(state[0])
        update_stats(state)
    else:
        try:
            state = next(solver_generator)
            debug_history.append(state)
            debug_step += 1
            update_grid(state[0])
            update_stats(state)
            
            if state[2] != "searching":
                btn_right.config(state="disabled")
        except StopIteration:
            pass


def step_backward():
    global debug_step
    if debug_step > 0:
        debug_step -= 1
        state = debug_history[debug_step]
        update_grid(state[0])
        update_stats(state)
        btn_right.config(state="normal")


def finish_debug():
    global debug_step
    last_state = None
    for state in solver_generator:
        last_state = state
        debug_history.append(state)
        if state[2] != "searching":
            break
            
    if last_state:
        debug_step = len(debug_history) - 1
        update_grid(last_state[0])
        update_stats(last_state)
        btn_right.config(state="disabled")


def update_grid(assignment):
    for (r, c), btn in grid_buttons.items():
        val = assignment.get((r, c))
        if val == 1:
            btn.config(bg="black", text="✅")
        elif val == 0:
            btn.config(bg="white", text="")
        else:
            btn.config(bg="white", text="")


def update_stats(state, exec_time=None):
    assignment, nodes, status = state
    text = f"Nodes Visited: {nodes} | Status: {status.replace('_', ' ').title()}"
    if exec_time is not None:
        text += f" | Time: {exec_time:.4f}s"
    stats_label.config(text=text)


def update_heuristic_dropdown(algo, dropdown, var):
    if algo == "Backtracking Search":
        dropdown.config(state="normal")
    else:
        var.set("None")
        dropdown.config(state="disabled")


# Create main window
root = tk.Tk()
root.title("Kakurasu Puzzle Solver")
root.attributes("-fullscreen", True)

# Allow exiting full screen with Escape key
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

# Top frame for the button
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, pady=20)

load_btn = tk.Button(
    top_frame, text="Select .txt File", command=load_file, font=("Arial", 14)
)
load_btn.pack(anchor=tk.CENTER)

# Frame for the grid
grid_frame = tk.Frame(root)
grid_frame.pack(expand=True)

# Stats Label
stats_label = tk.Label(root, text="", font=("Arial", 14, "bold"))
stats_label.pack(pady=10)

# Frame for the controls (dropdowns and start button)
controls_frame = tk.Frame(root)
controls_frame.pack(side=tk.BOTTOM, pady=40)

# Frame for debug mode controls
debug_frame = tk.Frame(root)
btn_left = tk.Button(debug_frame, text="< Step Backward", font=("Arial", 14), command=step_backward)
btn_left.grid(row=0, column=0, padx=10)
btn_right = tk.Button(debug_frame, text="Step Forward >", font=("Arial", 14), command=step_forward)
btn_right.grid(row=0, column=1, padx=10)
btn_finish = tk.Button(debug_frame, text="Finish", font=("Arial", 14, "bold"), bg="blue", fg="white", command=finish_debug)
btn_finish.grid(row=0, column=2, padx=10)

# Run the app
root.mainloop()
