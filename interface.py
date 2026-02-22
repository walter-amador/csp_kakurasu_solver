import tkinter as tk
from tkinter import filedialog, messagebox


def load_file():
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not filepath:
        return

    try:
        with open(filepath, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if len(lines) != 3:
            raise ValueError("File must have exactly 3 rows.")

        n = int(lines[0])
        row_targets = [int(x) for x in lines[1].split(",")]
        col_targets = [int(x) for x in lines[2].split(",")]

        if len(row_targets) != n or len(col_targets) != n:
            raise ValueError(
                f"Rows 2 and 3 must have exactly {n} comma-separated numbers."
            )

        draw_grid(n, row_targets, col_targets)
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
    load_btn.config(text="Select .txt File", command=load_file)


def draw_grid(n, row_targets, col_targets):
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

# Run the app
root.mainloop()
