# **STEGNO IMAGE VIEWER**  

## **Overview**  
SecureView is a **steganography-based gallery app** built with **Kivy and Python** that allows users to **hide encrypted messages inside PNG images**. These images can be **shared through any platform** (email, messaging apps, USB, etc.) while keeping the hidden message undetectable. To retrieve the message, the recipient must **install SecureView**, open the image, and press **Volume Down or F11** to decode it.  

This method ensures **secure and private communication**, making it useful for **confidential messaging, cybersecurity learning, and personal data storage**.  

---

## **Key Features**  

✔ **Gallery & Image Viewer** – View, store, and manage PNG images.  
✔ **Message Embedding** – Hide encrypted text inside images before sharing.  
✔ **Universal Sharing** – Send steganographic PNG images via any platform.  
✔ **Trigger-Based Decoding** – Press **Volume Down or F11** while viewing the image to reveal the hidden message.  
✔ **AES/RSA Encryption** – Encrypts messages for secure storage inside images.  
✔ **User-Friendly Interface** – Simple and smooth UI built with **Kivy** for cross-platform use.  

---

## **How It Works**  

### **1. Hiding a Message (Sender Side)**  
- Open an image or capture a new one.  
- Press a special trigger (e.g., a hidden button or an option in the menu).  
- Enter the secret message in the provided text box.  
- SecureView encrypts the message using **AES/RSA encryption**.  
- The encrypted message is hidden inside the image using **LSB (Least Significant Bit) steganography**.  
- The modified **PNG image is saved** and can be **sent via any method (WhatsApp, Email, USB, Cloud, etc.)**.  

### **2. Retrieving a Message (Receiver Side)**  
- Install SecureView and open the received **PNG image** in the gallery.  
- Press **Volume Down or F11** while viewing the image.  
- SecureView will **extract and decrypt the message**, revealing it on the screen.  
- If the image has no hidden message, nothing will be displayed.  

---

## **Tech Stack**  

- **Framework:** Kivy (Python)  
- **Encryption:** AES/RSA for secure message storage  
- **Steganography:** LSB-based encoding for message concealment  
- **Storage:** Local storage for images and encrypted messages  
- **Security Measures:** Key-based decryption to prevent unauthorized access  

---

## **Use Cases**  

🔹 **Confidential Communication** – Share hidden messages securely.  
🔹 **Personal Data Storage** – Store private notes in images.  
🔹 **Covert Messaging** – Disguise sensitive information in PNG images.  
🔹 **Cybersecurity & Steganography Learning** – An educational tool for encryption enthusiasts.  

---

## **Security & Limitations**  

🔒 **Security Considerations:**  
- Only users with **SecureView installed** can decode hidden messages.  
- Messages are **fully encrypted** before embedding into images.  

⚠ **Limitations:**  
- Modifying the image **after embedding** (e.g., cropping, compressing) may destroy the hidden message.  
- Large messages may slightly affect image quality.  

---

## **License**  
SecureView is an open-source project licensed under the [MIT License](LICENSE).  

---
## **Video Link**  
https://drive.google.com/file/d/1EM7pYYUXpUAlTcQWSmSMxG3q5ORV6yzY/view?usp=drive_link  
