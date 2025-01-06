# Control Spotify with Hand Gestures

# **Overview**

The goal of this project was to develop a gesture-based system for media control using a laptop camera, leveraging computer vision to translate hand movements into commands like play/pause, skip, rewind, and volume adjustments. This system utilized the MediaPipe library for real-time hand tracking and AppleScript for controlling Spotify, ultimately achieving the intended functionality, although with compromises.

## **Implementation Details**

The project began with setting up the webcam feed using OpenCV and integrating MediaPipe for hand tracking. MediaPipe provided a set of 21 hand landmarks representing key points on the hand, including the wrist, joints, and fingertips. These landmarks, identified by specific indices, were critical to developing gesture recognition logic.

https://lh7-rt.googleusercontent.com/docsz/AD_4nXclmCX4CXBijZuoULlZw7YCKPTbrpfXbPwx-GIIoxEqdtAwJYBaOQarCySUaWPYvDkwP3zuV1S3F2C0sxrCvJqYGG8OqcmkFo49xRW1dWgqWaLvj9DZkBtdFdyUa6n553uV82B4qQ?key=hNQASpI_PLOQ7nTy6e7mk5D0

## **Initial Gesture Recognition**

The first step was to determine when fingers were raised. I identified a pattern using the distances between specific landmarks. For instance, a finger was considered raised if the distance between its base joint (e.g., landmark 5 for the index finger) and its fingertip (e.g., landmark 8 for the index finger) was greater than half the distance between the wrist (landmark 0) and the base joint of the middle finger (landmark 9). This adaptive threshold ensured accuracy across different hand sizes and varying distances from the camera.

https://lh7-rt.googleusercontent.com/docsz/AD_4nXfMGSpiJS0RPmIpdDKMwUSlovu2gcJM-hDn3jwMH2-henXDMmm6jE-kR9DIemgOQ22xjNJYZI3jB2RytrO3gBKKTXZ2p_dVqN6Z1pxMOKk8XK5GN1jppBiakAC6u0b1AdDzcdUJ?key=hNQASpI_PLOQ7nTy6e7mk5D0

This process required significant trial and error. Initially, I tested fixed pixel thresholds, but they failed when the hand moved closer or farther from the camera. By anchoring the threshold to relative hand proportions, I achieved consistent results across various scenarios. Testing involved waving my hand at different angles, distances, and positions in the camera’s field of view to fine-tune the logic.

## **Volume Control with Pinch Gesture**

For volume adjustment, I implemented a pinch gesture based on the distance between the thumb tip (landmark 4) and the index finger tip (landmark 8). The challenge here was to map this distance to a percentage value for volume, regardless of hand size or camera position. Through experimentation, I found that using the sum of distances between the wrist (landmark 0) to the thumb base (landmark 5) and from the thumb base (landmark 5) to the thumb joint (landmark 6) provided a reliable reference scale. The ratio of the pinch distance to this reference scale produced a percentage value that intuitively represented volume levels.

https://lh7-rt.googleusercontent.com/docsz/AD_4nXeKKjAaxdDveGIe6hXggLd7cwOi_uWgxiZ2u-EV-4wY4ETcwFPgvODbr3gDtvdk-c5ZyO88n12nccEy6zCu8c79yZjyorF0BD7PXArwilA2Gh10R9OaejiyKXwg7d-ae-GtGDm-ow?key=hNQASpI_PLOQ7nTy6e7mk5D0

Several alternatives were tested, such as using the distance from the wrist (landmark 0) to the base of the middle finger (landmark 9) similar to the raised finger technique as the reference, but these proved less intuitive during testing and would either mute or max out the volume to early. Ultimately, the chosen method aligned well with natural hand gestures and provided a smooth volume adjustment experience.

## **Integrating Media Controls**

For play, pause, skip, and rewind functions, I initially planned to simulate keyboard shortcuts using combinations like such as + F8. However, MacOS restrictions on simulating the FN key led me to explore alternative methods. After testing various libraries and having little success, I discovered AppleScript, which allowed direct control of Spotify. This workaround simplified command execution but limited functionality to Spotify, as AppleScript requires targeting a specific application. At this point, I decided on my set of gestures:

- **Play/Pause:** 4 fingers raised.
- **Skip:** 1 finger raised.
- **Rewind:** 2 fingers raised.
- **Volume: Distance between thumb and pointer finger**

## **Addressing Conflicts Between Gestures**

Combining finger-raising gestures and pinch gestures for simultaneous use presented a significant challenge. The system tracked all 21 landmarks continuously, which led to conflicts when gestures overlapped. For example, a raised finger during the volume pinch gesture would sometimes register as a media control gesture. Or when trying to pause the music by raising all fingers, it would set the volume to max. This was the biggest roadblock of the project and required lots of trial and error and required me to be quite creative.

To resolve this, I devised a toggle mechanism based on the angle between thumb joints:

- If the angle between landmarks 2 (thumb MCP), 3 (thumb IP), and 4 (thumb tip) was less than 180 degrees, the thumb was extended. With the thumb extended, the system would exclusively recognize the pinch gesture for volume control.
- If the angle was greater than 180 degrees, the thumb was bent. With the thumb bent, the system would exclusively recognize the finger-raising gestures for media controls.

https://lh7-rt.googleusercontent.com/docsz/AD_4nXfTUH_jz1p_h0xDHZRqWVjgQ1deRP5wlivPgZwfW4itdPHCyzeAeOGdylhaRe2k-Cs-uEnjNXYm4MEByj6U83mlcDOKZvPAciHDjXJmBrxqIZ9fBECRUHO2oAUnOFaoN4FHXU1D?key=hNQASpI_PLOQ7nTy6e7mk5D0

This toggle system, while a compromise of the original plan, ensured intuitive transitions between the two gesture types.

## **Stabilizing Gesture Detection**

A recurring issue was unintended gesture activation when raising the hand into the camera’s view. To address this, I implemented a stability check based on the wrist (landmark 0). The system measured the movement of the wrist across frames, and a gesture was only processed if the wrist remained within a small movement threshold for 15 consecutive frames. Testing involved simulating everyday scenarios, such as scratching my head or itching my eye, to ensure the system could differentiate between intentional and unintentional gestures.

## **Performance Optimization**

Processing gesture recognition logic for every camera frame at 30 FPS was computationally intensive, leading to performance bottlenecks. I reduced the frequency of gesture processing to 10 evaluations per second while keeping the camera feed at 30 FPS. This optimization balanced system responsiveness and computational load, ensuring smooth performance during use.

# **Final Outcome**

The project achieved a functional prototype capable of controlling Spotify using gestures. Key features included:

- Play/Pause/Skip/Rewind based on different raised finger counts.
- Volume adjustment via an intuitive pinch gesture with a scaling mechanism.

However, the system is limited to Spotify due to AppleScript integration. Furthermore, gestures for volume and media control require explicit toggling based on thumb position due to conflicts in real-time tracking.

While the final system diverged from the original plan, it serves as a solid proof of concept for gesture-based media control. This project was deeply rewarding because it allowed me to work on something I was genuinely interested in and could see a real use case for. The concept of controlling media with hand gestures has always fascinated me, and bringing it to life tested not only my technical skills but also my creativity in problem-solving.

Throughout the development process, I encountered challenges that required me to think outside the box, experiment with different approaches, and refine my implementation from calibrating hand landmarks to designing gesture logic that balanced usability and precision. I gained a better understanding of computer vision, explored new tools like MediaPipe and AppleScript, and learned the importance of adapting plans as new constraints emerged.

While there are improvements I would like to make in the future such as implementing more advanced gestures or leveraging machine learning to better distinguish gesture contexts, I am very happy with where this project ended up.
