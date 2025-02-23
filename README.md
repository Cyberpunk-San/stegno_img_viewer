# stegno_img_viewer
Project Name: SecureView – Encrypted Image Messenger

Description:

SecureView is a steganography-based image viewer app built with Kivy and Python. It allows users to securely hide messages inside images using encryption and retrieve them with a one-time key. The app functions as a normal image viewer and camera but includes a secret trigger mechanism for encoding and decoding hidden messages.

Key Features:

✅ Image Viewer & Camera – View images and capture photos seamlessly.
✅ Steganography-Based Encryption – Hide secret messages inside images.
✅ Trigger Mechanism for Message Input – Pressing a specific button (e.g., volume button) opens a textbox for entering a hidden message.
✅ One-Time Key Generation – Encrypts the message and provides a unique key for secure retrieval.
✅ Secure Decryption – The recipient presses the trigger button and enters the one-time key to reveal the message.
✅ User-Friendly Kivy UI – Smooth, responsive, and cross-platform interface.

Tech Stack:

Framework: Kivy (Python)

Encryption: AES/RSA for secure message storage

Steganography: LSB-based encoding to hide messages inside images

Storage: Local storage for images and encrypted data

Security Measures: Ensures confidentiality with key-based decryption

Use Cases:

🔹 Confidential Communication – Securely share sensitive messages.
🔹 Personal Data Storage – Hide private notes inside images.
🔹 Cybersecurity & Steganography Learning – Educational tool for encryption enthusiasts.
