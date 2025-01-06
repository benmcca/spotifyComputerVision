import cv2
import mediapipe as mp
import time
import math
import subprocess

# Function to count fingers raised based on hand landmarks
def count_fingers(hand_landmarks):
    count = 0
    # Calculate the threshold for finger detection (half of the distance between palm and bottom of middle finger)
    thresh = (hand_landmarks.landmark[0].y * 100 - hand_landmarks.landmark[9].y * 100) / 2

    # Detect fingers raised based on landmark positions
    if (hand_landmarks.landmark[5].y * 100 - hand_landmarks.landmark[8].y * 100) > thresh:
        count += 1
    if (hand_landmarks.landmark[9].y * 100 - hand_landmarks.landmark[12].y * 100) > thresh:
        count += 1
    if (hand_landmarks.landmark[13].y * 100 - hand_landmarks.landmark[16].y * 100) > thresh:
        count += 1
    if (hand_landmarks.landmark[17].y * 100 - hand_landmarks.landmark[20].y * 100) > thresh:
        count += 1

    return count

# Function to determine if the angle between thumb joint is less or more than 180 degrees
# Function to determine if the angle between thumb joint is less or more than 180 degrees
def is_angle_less_than_180(hand_landmarks):
    # Extract coordinates of the points
    p4 = hand_landmarks.landmark[4]  # Thumb tip
    p3 = hand_landmarks.landmark[3]  # Thumb joint
    p2 = hand_landmarks.landmark[2]  # Pointer finger joint
    p1 = hand_landmarks.landmark[1]  # Thumb base
    p0 = hand_landmarks.landmark[0]  # Wrist

    # Calculate vectors for the two lines
    vec_43 = (p4.x - p3.x, p4.y - p3.y)
    vec_32 = (p2.x - p3.x, p2.y - p3.y)

    # Compute the cross product to determine angle orientation
    cross_product = vec_43[0] * vec_32[1] - vec_43[1] * vec_32[0]

    # Compute the dot product to determine the angle magnitude
    dot_product = vec_43[0] * vec_32[0] + vec_43[1] * vec_32[1]

    # Calculate magnitudes of the vectors
    magnitude_43 = math.sqrt(vec_43[0]**2 + vec_43[1]**2)
    magnitude_32 = math.sqrt(vec_32[0]**2 + vec_32[1]**2)

    # Use the dot product and magnitudes to calculate cosine of the angle
    cos_theta = dot_product / (magnitude_43 * magnitude_32)

    # Determine if it is a left hand or right hand based on x-coordinates
    if p1.x > p0.x:
        # Left hand: Reverse the angle check outcome
        return cross_product > 0
    else:
        # Right hand: Use the original angle check outcome
        return cross_product < 0

# Calculate the Euclidean distance between two points
def calculate_distance(point1, point2, frame_width, frame_height):
    x1, y1 = int(point1.x * frame_width), int(point1.y * frame_height)
    x2, y2 = int(point2.x * frame_width), int(point2.y * frame_height)
    
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return distance

# Check if the wrist is stable by comparing its movement across frames
def is_wrist_stable(wrist_position, prev_wrist_position, frame_width, frame_height, threshold):
    # Get positions of current and previous wrist position
    x1, y1 = int(wrist_position.x * frame_width), int(wrist_position.y * frame_height)
    x2, y2 = int(prev_wrist_position.x * frame_width), int(prev_wrist_position.y * frame_height)
    
    # Check if distance is less than the movement threshold
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return distance <= threshold

# Control media playback on Spotify using AppleScript
def control_media(action):
    if action == "play_pause":
        applescript = 'tell application "Spotify" to playpause'
    elif action == "next":
        applescript = 'tell application "Spotify" to next track'
    elif action == "previous":
        applescript = 'tell application "Spotify" to previous track'
    else:
        raise ValueError("Invalid action. Choose from 'play_pause', 'next', 'previous'.")

    # Execute the AppleScript command using osascript
    subprocess.run(["osascript", "-e", applescript])

# Set macOS system volume using AppleScript (input integer between 0 and 10)
def set_system_volume(volume_ratio):
    # Scale volume_ratio to macOS volume range (0 to 100)
    volume_level = int(min(max(volume_ratio * 10, 0), 100))  # Ensure it's between 0 and 100
    
    # AppleScript to set the system volume
    applescript = f'set volume output volume {volume_level}'
    
    # Execute the AppleScript command using osascript
    subprocess.run(["osascript", "-e", applescript])

cap = cv2.VideoCapture(0)
# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
scale_factor = 0.75

drawing = mp.solutions.drawing_utils
hands = mp.solutions.hands
hand_obj = hands.Hands(max_num_hands=1)

last_action_time = time.time()  # Initialize the time of the last action
last_logic_time = time.time()

# Initialize variables
prev_wrist_position = None
wrist_stable_text = "Not stable"
angle_text = "Volume"
gesture_status_text = "Fingers: 0"
stability_threshold = 25 # Wrist can not move more than x pixels to be considered stable
stable_frame_count = 0  # Counter for stable frames
required_stable_frames = 15  # Number of consecutive stable frames required to be considered stable
volumeRatio = 0

while True:
    ret, frm = cap.read()

    # Verify that frame was captured
    if not ret:
        print("Failed to grab frame.")
        break

    # Mirror image
    frm = cv2.flip(frm, 1)

    # Process the frame if it's not empty
    res = hand_obj.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

    # If hand detected
    if res.multi_hand_landmarks:
        hand_keyPoints = res.multi_hand_landmarks[0]

        # Get the wrist position
        current_wrist_position = hand_keyPoints.landmark[0]
        isWristStable = False

        # Check wrist stability
        if prev_wrist_position is not None:
            h, w, _ = frm.shape  # Get frame dimensions
            isWristStable = is_wrist_stable(current_wrist_position, prev_wrist_position, w, h, threshold=stability_threshold)
            
            # Update stability counter
            if isWristStable:
                stable_frame_count += 1
            else:
                stable_frame_count = 0

        # Update the previous wrist position
        prev_wrist_position = current_wrist_position

        # Check if wrist is stable for enough consecutive frames
        wrist_considered_stable = stable_frame_count >= required_stable_frames
        wrist_stable_text = "Stable" if wrist_considered_stable else "Not stable"

        # Perform gesture logic only if wrist is considered stable
        if wrist_considered_stable:
            # Perform your existing gesture logic
            if time.time() - last_logic_time >= 0.1:

                # Angle less than 180 means that we are in volume mode
                if is_angle_less_than_180(hand_keyPoints):
                    angle_text = "Volume"
                    
                    # Calculate the distance between thumb tip and pointer tip
                    distance48 = calculate_distance(hand_keyPoints.landmark[4], hand_keyPoints.landmark[8], w, h)

                    # Calculate the total distance between wrist and joint on pointer finger
                    distance05 = calculate_distance(hand_keyPoints.landmark[0], hand_keyPoints.landmark[5], w, h)
                    distance56 = calculate_distance(hand_keyPoints.landmark[5], hand_keyPoints.landmark[6], w, h)
                    distance056 = distance05 + distance56

                    volumeRatio = distance48 / distance056
                    volumeRatio -= 0.1
                    volumeRatio = int(round(volumeRatio, 1) * 10)
                    volumeRatio = int(min(max(volumeRatio, 0), 10))

                    set_system_volume(volumeRatio)
                    gesture_status_text = f"Volume: {volumeRatio}"
                    last_logic_time = time.time()

                # Angle more than 180 means that we are in control mode
                else:
                    angle_text = "Control"
                    fingers = count_fingers(hand_keyPoints)
                    gesture_status_text = f"Fingers: {fingers}"

                    # Enforce 1.5 second cool down between actions
                    if time.time() - last_action_time >= 1.5:
                        # All fingers raised, play/pause
                        if fingers == 4:
                            control_media("play_pause")
                            last_action_time = time.time()
                        # One finger raised, skip
                        elif fingers == 1:
                            control_media("next")
                            last_action_time = time.time()
                        # Two fingers raised, previous
                        elif fingers == 2:
                            control_media("previous")
                            last_action_time = time.time()

        # Add text to the frame
        cv2.putText(frm, wrist_stable_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 0) if wrist_stable_text == "Stable" else (0, 0, 255), 2, cv2.LINE_AA)

        # Gesture Status
        cv2.putText(frm, gesture_status_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 0, 0), 2, cv2.LINE_AA)

        # Display the angle status
        cv2.putText(frm, angle_text, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (255, 255, 0), 2, cv2.LINE_AA)

        # Display hand connections
        drawing.draw_landmarks(frm, hand_keyPoints, hands.HAND_CONNECTIONS)

        if is_angle_less_than_180(hand_keyPoints):
            # Draw a line between thumb tip and pointer tip
            thumb_tip = hand_keyPoints.landmark[4]
            pointer_tip = hand_keyPoints.landmark[8]

            # Convert normalized landmark positions to pixel coordinates
            thumb_x, thumb_y = int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height)
            pointer_x, pointer_y = int(pointer_tip.x * frame_width), int(pointer_tip.y * frame_height)

            # Draw the line on the frame
            cv2.line(frm, (thumb_x, thumb_y), (pointer_x, pointer_y), (255, 0, 0), 3)

    # Show the updated frame
    frm = cv2.resize(frm, (int(frame_width * scale_factor), int(frame_height * scale_factor)))
    cv2.imshow("window", frm)

    # Exit on pressing 'ESC' (key code 27)
    if cv2.waitKey(1) == 27:
        break

# Release resources after the loop
cap.release()
cv2.destroyAllWindows()
