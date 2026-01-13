import cv2
import mediapipe as mp
import numpy as np
import time
import threading

def play_beep():
    try:
        import os
        if os.name == 'nt':
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            print('\a')
    except:
        pass

def calculate_angle(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def run(mode="free", target_reps=None, target_time=None):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera!")
        return {"reps": 0, "good_reps": 0, "wrong_reps": 0, "avg_angle": 0}

    mp_pose = mp.solutions.pose
    mp_draw = mp.solutions.drawing_utils
    window_name = "Squat Exercise"

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

        # ─── CALIBRATION PHASE ───────────────────────────────────────────────
        print("Calibration: Please stand straight with feet shoulder-width apart, arms relaxed.")
        calib_angles = []
        calib_start = time.time()
        CALIB_DURATION = 4.0  # seconds

        while cap.isOpened() and (time.time() - calib_start) < CALIB_DURATION:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)
            frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            angle = 0

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                key_points = [
                    lm[mp_pose.PoseLandmark.LEFT_HIP], lm[mp_pose.PoseLandmark.LEFT_KNEE], lm[mp_pose.PoseLandmark.LEFT_ANKLE],
                    lm[mp_pose.PoseLandmark.RIGHT_HIP], lm[mp_pose.PoseLandmark.RIGHT_KNEE], lm[mp_pose.PoseLandmark.RIGHT_ANKLE]
                ]
                avg_visibility = np.mean([p.visibility for p in key_points if p.visibility > 0])

                if avg_visibility > 0.6:
                    left_vis = np.mean([lm[i].visibility for i in [23, 25, 27]])  # LEFT_HIP=23, KNEE=25, ANKLE=27
                    right_vis = np.mean([lm[i].visibility for i in [24, 26, 28]])

                    if right_vis >= left_vis and right_vis > 0.5:
                        hip   = [lm[24].x, lm[24].y]
                        knee  = [lm[26].x, lm[26].y]
                        ankle = [lm[28].x, lm[28].y]
                    elif left_vis > 0.5:
                        hip   = [lm[23].x, lm[23].y]
                        knee  = [lm[25].x, lm[25].y]
                        ankle = [lm[27].x, lm[27].y]
                    else:
                        continue

                    angle = calculate_angle(hip, knee, ankle)
                    calib_angles.append(angle)

                    mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    knee_px = (int(knee[0] * frame.shape[1]), int(knee[1] * frame.shape[0]))
                    cv2.circle(frame, knee_px, 15, (0, 255, 0), -1)

            cv2.putText(frame, "CALIBRATION - Stand straight!", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 3)
            cv2.putText(frame, f"Current knee angle: {int(angle)}°", (50, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
                cap.release()
                cv2.destroyAllWindows()
                return {"reps":0, "good_reps":0, "wrong_reps":0, "avg_angle":0}

        rest_angle = np.mean(calib_angles) if calib_angles else 175.0
        print(f"→ Rest angle (standing straight) detected: {rest_angle:.1f}°")

        # No 2-second display delay, proceed directly to exercise

        # ─── MAIN EXERCISE LOOP ──────────────────────────────────────────────
        reps = good_reps = wrong_reps = 0
        stage = None
        current_rep_min_angle = None
        rep_min_angles = []
        start_time = time.time() if target_time else None
        completed = False

        person_detected = False
        lost_tracking_start = None
        LOST_THRESHOLD = 2.0
        paused = False

        while cap.isOpened() and not completed:
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)
            frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            current_time = time.time()
            person_detected = False
            angle = 0

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                key_points = [
                    lm[mp_pose.PoseLandmark.LEFT_HIP], lm[mp_pose.PoseLandmark.LEFT_KNEE], lm[mp_pose.PoseLandmark.LEFT_ANKLE],
                    lm[mp_pose.PoseLandmark.RIGHT_HIP], lm[mp_pose.PoseLandmark.RIGHT_KNEE], lm[mp_pose.PoseLandmark.RIGHT_ANKLE]
                ]
                avg_visibility = np.mean([p.visibility for p in key_points])

                if avg_visibility > 0.6:
                    person_detected = True
                    lost_tracking_start = None
                    paused = False

                    left_visibility = np.mean([lm[23].visibility, lm[25].visibility, lm[27].visibility])
                    right_visibility = np.mean([lm[24].visibility, lm[26].visibility, lm[28].visibility])

                    if right_visibility >= left_visibility and right_visibility > 0.5:
                        hip   = [lm[24].x, lm[24].y]
                        knee  = [lm[26].x, lm[26].y]
                        ankle = [lm[28].x, lm[28].y]
                    elif left_visibility > 0.5:
                        hip   = [lm[23].x, lm[23].y]
                        knee  = [lm[25].x, lm[25].y]
                        ankle = [lm[27].x, lm[27].y]
                    else:
                        continue

                    angle = calculate_angle(hip, knee, ankle)
                    mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    knee_px = (int(knee[0] * frame.shape[1]), int(knee[1] * frame.shape[0]))
                    cv2.circle(frame, knee_px, 15, (0, 255, 0), -1)

                    if angle > 160:
                        if stage == "down":
                            reps += 1
                            if current_rep_min_angle is not None:
                                rep_min_angles.append(current_rep_min_angle)
                                if current_rep_min_angle < 85:
                                    good_reps += 1
                                else:
                                    wrong_reps += 1
                            current_rep_min_angle = None
                        stage = "up"

                    elif angle < 130:
                        if stage != "down":
                            stage = "down"
                            current_rep_min_angle = angle
                        else:
                            if angle < current_rep_min_angle:
                                current_rep_min_angle = angle

            if not person_detected:
                if lost_tracking_start is None:
                    lost_tracking_start = current_time
                elif current_time - lost_tracking_start > LOST_THRESHOLD and not paused:
                    paused = True

            # DISPLAY
            if mode == "reps" and target_reps:
                cv2.putText(frame, f"REPS: {reps}/{target_reps}", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
            else:
                cv2.putText(frame, f"REPS: {reps}", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

            if mode == "time" and target_time:
                elapsed = int(time.time() - start_time)
                remaining = max(0, target_time - elapsed)
                mins, secs = divmod(remaining, 60)
                cv2.putText(frame, f"TIME LEFT: {mins:02d}:{secs:02d}", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 3)

            cv2.putText(frame, f"ANGLE: {int(angle)}°", (20, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

            if paused:
                cv2.putText(frame, "COUNTING PAUSED", (20, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)
                cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), 10)

            cv2.imshow(window_name, frame)

            if mode == "reps" and target_reps and reps >= target_reps:
                cv2.putText(frame, f"COMPLETED {target_reps} REPS!", (80, 300),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 5)
                cv2.imshow(window_name, frame)
                cv2.waitKey(4000)
                completed = True

            if mode == "time" and target_time and (time.time() - start_time) >= target_time:
                cv2.putText(frame, f"TIME UP! {reps} REPS", (100, 300),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 5)
                cv2.imshow(window_name, frame)
                cv2.waitKey(4000)
                completed = True

            if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
                break

    cap.release()
    cv2.destroyAllWindows()

    avg_angle = np.mean(rep_min_angles) if rep_min_angles else 0
    return {
        "reps": reps,
        "good_reps": good_reps,
        "wrong_reps": wrong_reps,
        "avg_angle": round(avg_angle, 1) if avg_angle else 0
    }