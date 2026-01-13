
import tkinter as tk
from tkinter import messagebox

import exercisessquat
import exercisesarm_raise
import exercises_bicep_curl
from evaluation import show_evaluation
from history import save_session, get_history

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ================= HÀM KHỞI ĐỘNG LẠI MENU =================
def restart_menu():
    global root
    try:
        if root.winfo_exists():
            root.destroy()
    except:
        pass
    root = tk.Tk()
    setup_ui()
    root.mainloop()

# ================= HÀM XEM TIẾN ĐỘ =================
def show_progress():
    exercises = ["SQUAT", "ARM RAISE", "BICEP CURL"]
    
    win = tk.Toplevel(root)
    win.title("Tiến Độ Tập Luyện")
    win.geometry("800x600")
    win.configure(bg="#0f172a")
    win.resizable(True, True)
    
    tk.Label(win, text="📊 TIẾN ĐỘ TẬP LUYỆN", font=("Segoe UI", 22, "bold"),
             fg="#38bdf8", bg="#0f172a").pack(pady=25)
    
    tk.Label(win, text="Chọn bài tập để xem biểu đồ tiến độ theo thời gian", 
             font=("Segoe UI", 13), fg="#94a3b8", bg="#0f172a").pack(pady=(0, 20))
    
    frame_select = tk.Frame(win, bg="#0f172a")
    frame_select.pack(pady=10)
    
    tk.Label(frame_select, text="Bài tập:", font=("Segoe UI", 14), fg="white", bg="#0f172a").pack(side=tk.LEFT, padx=10)
    
    selected_exercise = tk.StringVar(value=exercises[0])
    dropdown = tk.OptionMenu(frame_select, selected_exercise, *exercises)
    dropdown.config(font=("Segoe UI", 12), width=20, bg="#1e293b", fg="white", bd=0, highlightthickness=0)
    dropdown.pack(side=tk.LEFT, padx=10)
    
    display_frame = tk.Frame(win, bg="#0f172a")
    display_frame.pack(pady=30, fill=tk.BOTH, expand=True)
    
    def plot_graph():
        for widget in display_frame.winfo_children():
            widget.destroy()
        
        exercise = selected_exercise.get()
        hist = get_history(exercise)
        
        if not hist:
            tk.Label(display_frame, 
                     text="⚠️ Chưa có dữ liệu!\n\nHãy tập ít nhất 1 buổi bài tập này để bắt đầu theo dõi tiến độ.",
                     font=("Segoe UI", 16), fg="#fbbf24", bg="#0f172a", justify="center").pack(expand=True)
            return
        
        if len(hist) == 1:
            entry = hist[0]
            tk.Label(display_frame,
                     text=f"✅ Đã có 1 buổi tập!\n\n"
                          f"Ngày: {entry['date']}\n"
                          f"Số reps: {entry['reps']}\n"
                          f"Độ chính xác: {entry['accuracy']}%\n"
                          f"Góc trung bình: {entry['avg_angle']:.1f}°\n\n"
                          f"📈 Tập thêm vài buổi nữa để thấy biểu đồ đường đẹp mắt nhé!",
                     font=("Segoe UI", 15), fg="#86efac", bg="#0f172a", justify="center").pack(expand=True)
            return
        
        dates_str = [entry["date"] for entry in hist]
        accuracy = [entry["accuracy"] for entry in hist]
        reps = [entry["reps"] for entry in hist]
        avg_angles = [entry["avg_angle"] for entry in hist]
        
        dates = [datetime.strptime(d, "%d/%m/%Y %H:%M") for d in dates_str]
        
        plt.figure(figsize=(12, 7))
        plt.style.use('dark_background')
        
        plt.plot(dates, accuracy, marker='o', markersize=12, linewidth=4, 
                 color='#22c55e', label='Độ chính xác (%)', zorder=3)
        
        plt.plot(dates, reps, marker='s', markersize=10, linewidth=3, 
                 color='#3b82f6', label='Số reps', zorder=2)
        
        for i, (d, acc, r) in enumerate(zip(dates, accuracy, reps)):
            plt.text(d, acc + 2, f"{acc}%", ha='center', va='bottom', 
                     fontsize=11, fontweight='bold', color='#22c55e')
            plt.text(d, r + 2, f"{r}", ha='center', va='bottom', 
                     fontsize=11, fontweight='bold', color='#3b82f6')
        
        plt.title(f"Tiến độ Tập Luyện - {exercise}", fontsize=20, color='#38bdf8', pad=30)
        plt.xlabel("Thời gian", fontsize=14, color='white')
        plt.ylabel("Giá trị", fontsize=14, color='white')
        
        plt.legend(fontsize=13, loc='upper left', framealpha=0.8)
        plt.grid(True, alpha=0.3, linestyle='--', color='#475569')
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m\n%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
        plt.xticks(rotation=0, ha='center')
        
        max_y = max(max(accuracy), max(reps)) + 15
        plt.ylim(0, max(100, max_y))
        
        latest_angle = avg_angles[-1]
        plt.text(0.02, 0.02, f"Góc TB gần nhất: {latest_angle:.1f}°", 
                 transform=plt.gca().transAxes, fontsize=12, color='#facc15',
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#1e293b", alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    tk.Button(win, text="📈 VẼ BIỂU ĐỒ TIẾN ĐỘ", font=("Segoe UI", 16, "bold"),
              width=30, height=2, bg="#22c55e", fg="white", bd=0, cursor="hand2",
              command=plot_graph).pack(pady=30)
    
    plot_graph()

# ================= CHỌN CHẾ ĐỘ SAU KHI CHỌN BÀI TẬP =================
def open_mode_selection(exercise_name, run_function):
    mode_win = tk.Toplevel(root)
    mode_win.title(f"Chế độ tập - {exercise_name}")
    mode_win.geometry("450x650")
    mode_win.configure(bg="#0f172a")
    mode_win.grab_set()
    mode_win.transient(root)

    tk.Label(mode_win, text=exercise_name, font=("Segoe UI", 26, "bold"),
             fg="#38bdf8", bg="#0f172a").pack(pady=30)

    tk.Label(mode_win, text="Chọn chế độ tập luyện", font=("Segoe UI", 16),
             fg="white", bg="#0f172a").pack(pady=10)

    selected_mode = tk.StringVar(value="free")

    # Fixed Reps
    tk.Radiobutton(mode_win, text="🎯 Tập đúng số reps mục tiêu", variable=selected_mode, value="reps",
                   font=("Segoe UI", 14), fg="white", bg="#0f172a", selectcolor="#1e293b").pack(pady=15, anchor="w", padx=80)
    
    reps_frame = tk.Frame(mode_win, bg="#0f172a")
    reps_frame.pack(pady=5)
    reps_var = tk.IntVar(value=10)
    tk.Label(reps_frame, text="Số reps:", fg="white", bg="#0f172a", font=("Segoe UI", 13)).pack(side=tk.LEFT)
    tk.Spinbox(reps_frame, from_=5, to=50, increment=1, textvariable=reps_var, width=6,
               font=("Segoe UI", 13)).pack(side=tk.LEFT, padx=15)

    # Timed Mode
    tk.Radiobutton(mode_win, text="⏱ Tập trong thời gian cố định", variable=selected_mode, value="time",
                   font=("Segoe UI", 14), fg="white", bg="#0f172a", selectcolor="#1e293b").pack(pady=15, anchor="w", padx=80)
    
    time_frame = tk.Frame(mode_win, bg="#0f172a")
    time_frame.pack(pady=5)
    time_var = tk.IntVar(value=60)
    tk.Label(time_frame, text="Thời gian:", fg="white", bg="#0f172a", font=("Segoe UI", 13)).pack(side=tk.LEFT)
    tk.Spinbox(time_frame, from_=30, to=300, increment=15, textvariable=time_var, width=6).pack(side=tk.LEFT, padx=15)
    tk.Label(time_frame, text="giây", fg="white", bg="#0f172a", font=("Segoe UI", 13)).pack(side=tk.LEFT, padx=5)

    # Free Mode
    tk.Radiobutton(mode_win, text="🆓 Tập tự do (nhấn Q để dừng)", variable=selected_mode, value="free",
                   font=("Segoe UI", 14), fg="white", bg="#0f172a", selectcolor="#1e293b").pack(pady=25, anchor="w", padx=80)

    def start_exercise():
        mode = selected_mode.get()
        target_reps = reps_var.get() if mode == "reps" else None
        target_time = time_var.get() if mode == "time" else None
        
        mode_win.destroy()
        root.withdraw()  
        
        data = run_function(mode=mode, target_reps=target_reps, target_time=target_time)
        
        save_session(exercise_name, data)
        show_evaluation(data, exercise_name, back_callback=lambda: [root.deiconify()])

    tk.Button(mode_win, text="🚀 BẮT ĐẦU TẬP", font=("Segoe UI", 18, "bold"), width=20, height=2,
              bg="#22c55e", fg="white", bd=0, cursor="hand2", command=start_exercise).pack(pady=50)

    tk.Button(mode_win, text="⬅ Quay lại menu", font=("Segoe UI", 12), bg="#6b7280", fg="white", width=15,
              command=mode_win.destroy).pack(pady=5)

# ================= SETUP GIAO DIỆN MENU =================
def setup_ui():
    root.title("Motion Analysis System")
    root.geometry("500x700")
    root.configure(bg="#0f172a")
    root.resizable(False, False)

    tk.Label(root, text="MOTION ANALYSIS", font=("Segoe UI", 22, "bold"),
             fg="#38bdf8", bg="#0f172a").pack(pady=40)

    tk.Label(root, text="Chọn bài tập", font=("Segoe UI", 14),
             fg="white", bg="#0f172a").pack(pady=10)

    tk.Button(root, text="🏋️ Squat", font=("Segoe UI", 15), width=20, height=2,
              bg="#22c55e", fg="white", bd=0,
              command=lambda: open_mode_selection("SQUAT", exercisessquat.run)).pack(pady=12)

    tk.Button(root, text="🙌 Arm Raise", font=("Segoe UI", 15), width=20, height=2,
              bg="#3b82f6", fg="white", bd=0,
              command=lambda: open_mode_selection("ARM RAISE", exercisesarm_raise.run)).pack(pady=12)

    tk.Button(root, text="💪 Bicep Curl", font=("Segoe UI", 15), width=20, height=2,
              bg="#f59e0b", fg="white", bd=0,
              command=lambda: open_mode_selection("BICEP CURL", exercises_bicep_curl.run)).pack(pady=12)

    tk.Button(root, text="📊 Xem Tiến Độ", font=("Segoe UI", 15), width=20, height=2,
              bg="#a855f7", fg="white", bd=0, command=show_progress).pack(pady=30)

    tk.Button(root, text="❌ Thoát", font=("Segoe UI", 12), width=12,
              bg="#ef4444", fg="white", bd=0, command=root.destroy).pack(pady=10)

# ================= KHỞI ĐỘNG =================
root = tk.Tk()
setup_ui()
root.mainloop()