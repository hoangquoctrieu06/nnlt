import tkinter as tk

def show_evaluation(data, exercise_name="Exercise", back_callback=None):
    reps = data["reps"]
    good = data["good_reps"]
    wrong = data["wrong_reps"]
    avg = data["avg_angle"]

    if reps == 0:
        grade = "F"
        comment = "No valid repetitions detected"
    else:
        accuracy = good / reps

        if exercise_name == "SQUAT":
            if accuracy >= 0.9 and avg <= 95:
                grade = "A"
                comment = "Excellent depth and form!"
            elif accuracy >= 0.75 and avg <= 110:
                grade = "B"
                comment = "Good squat, keep going deeper"
            elif accuracy >= 0.5:
                grade = "C"
                comment = "Needs more depth and consistency"
            else:
                grade = "D"
                comment = "Work on form and depth"

        elif exercise_name == "ARM RAISE":
            if accuracy >= 0.9 and avg >= 140:
                grade = "A"
                comment = "Perfect range of motion!"
            elif accuracy >= 0.75 and avg >= 120:
                grade = "B"
                comment = "Good, try to lower arm more"
            elif accuracy >= 0.5:
                grade = "C"
                comment = "Needs better range and control"
            else:
                grade = "D"
                comment = "Lower your arm fully next time"

        elif exercise_name == "BICEP CURL":  
            if accuracy >= 0.9 and avg >= 160:
                grade = "A"
                comment = "Perfect full range of motion!"
            elif accuracy >= 0.75 and avg >= 140:
                grade = "B"
                comment = "Good, try to fully extend arm"
            elif accuracy >= 0.5:
                grade = "C"
                comment = "Needs better extension and curl depth"
            else:
                grade = "D"
                comment = "Focus on full range - no swinging!"

        else:
            grade = "C"
            comment = "Completed exercise"

    # ===== GIAO DIỆN =====
    root = tk.Tk()
    root.title("Exercise Evaluation")
    root.geometry("450x550")
    root.configure(bg="#020617")
    root.resizable(False, False)

    tk.Label(root, text=f"{exercise_name} RESULT", font=("Segoe UI", 20, "bold"), fg="#38bdf8", bg="#020617").pack(pady=20)

    def info(text):
        tk.Label(root, text=text, font=("Segoe UI", 13), fg="white", bg="#020617").pack(pady=5)

    info(f"Total reps: {reps}")
    info(f"Correct reps: {good}")
    info(f"Wrong reps: {wrong}")
    info(f"Average critical angle: {avg:.1f}°")

    tk.Label(root, text=f"GRADE: {grade}", font=("Segoe UI", 28, "bold"),
             fg="#22c55e" if grade in ["A", "B"] else "#ef4444", bg="#020617").pack(pady=25)

    tk.Label(root, text=comment, font=("Segoe UI", 12, "italic"), fg="#facc15", bg="#020617").pack(pady=15)

    # ===== NÚT =====
    button_frame = tk.Frame(root, bg="#020617")
    button_frame.pack(pady=40)

    tk.Button(
        button_frame,
        text="🔄 Back to Menu",
        font=("Segoe UI", 11, "bold"),
        bg="#3b82f6",
        fg="white",
        bd=0,
        width=14,
        height=2,
        padx=10,
        pady=8,
        cursor="hand2",
        command=lambda: [root.destroy(), back_callback()] if back_callback else root.destroy()
    ).pack(side=tk.LEFT, padx=20)

    tk.Button(
        button_frame,
        text="❌ Close",
        font=("Segoe UI", 11),
        bg="#ef4444",
        fg="white",
        bd=0,
        width=12,
        height=2,
        padx=10,
        pady=8,
        cursor="hand2",
        command=root.destroy
    ).pack(side=tk.LEFT, padx=20)

    root.mainloop()