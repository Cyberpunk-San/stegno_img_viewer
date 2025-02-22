from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from cryptography.fernet import Fernet
import cv2
import os
from PIL import Image as PILImage, ImageEnhance, PngImagePlugin
from kivy.core.window import Window
import base64
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

class CameraApp(MDApp):
    def build(self):
        self.title = 'Camera App'
        
        # Main layout
        self.tabs = TabbedPanel(do_default_tab=False)  # Disable default tab
        
        # Camera Tab
        self.camera_tab = TabbedPanelItem(text='Camera')
        self.camera_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Camera feed
        self.camera_img = Image()
        self.camera_layout.add_widget(self.camera_img)
        
        # Capture button
        self.capture_btn = Button(text='Capture', size_hint=(1, 0.1))
        self.capture_btn.bind(on_press=self.capture)
        self.camera_layout.add_widget(self.capture_btn)
        
        # Add additional controls
        self.add_flash_control()
        self.add_zoom_control()
        self.add_timer_control()
        self.add_filter_controls()
        self.add_resolution_control()  # Add resolution control
        
        self.camera_tab.add_widget(self.camera_layout)
        self.tabs.add_widget(self.camera_tab)
        
        # Gallery Tab
        self.gallery_tab = TabbedPanelItem(text='Gallery')
        self.gallery_layout = BoxLayout(orientation='vertical')
        
        # Add image button
        self.add_image_btn = Button(text='Choose Image from Device', size_hint=(1, 0.1))
        self.add_image_btn.bind(on_press=self.open_file_chooser)  # Bind to open_file_chooser
        self.gallery_layout.add_widget(self.add_image_btn)
        
        # Scrollable gallery
        self.scroll_view = ScrollView()
        self.gallery_grid = GridLayout(cols=3, size_hint_y=None)
        self.gallery_grid.bind(minimum_height=self.gallery_grid.setter('height'))
        
        self.scroll_view.add_widget(self.gallery_grid)
        self.gallery_layout.add_widget(self.scroll_view)
        
        self.gallery_tab.add_widget(self.gallery_layout)
        self.tabs.add_widget(self.gallery_tab)
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            self.cap = None
        else:
            Clock.schedule_once(self.update, 1.0 / 30.0)  # Start the update loop
        
        Window.bind(on_key_down=self.on_key_down)
        self.selected_image_path = None
        
        return self.tabs

    def open_file_chooser(self, instance):
        # Create a file chooser popup
        self.file_chooser = FileChooserIconView()
        self.file_chooser.bind(on_selection=self.add_image_to_gallery)  # Bind selection to add_image_to_gallery
        
        # Create a popup to display the file chooser
        self.popup = Popup(title="Select Image", content=self.file_chooser, size_hint=(0.9, 0.9))
        self.popup.open()

    def add_image_to_gallery(self, file_chooser, selection):
        # Add the selected image to the gallery
        if selection:
            image_path = selection[0]
            if not os.path.exists('captured_images'):
                os.makedirs('captured_images')
            import shutil
            new_image_path = f'captured_images/{os.path.basename(image_path)}'
            shutil.copy(image_path, new_image_path)
            self.update_gallery(new_image_path)
            self.popup.dismiss()  # Close the popup after selection

    def update_gallery(self, image_path):
        # Add the image to the gallery grid
        img = Image(source=image_path, size_hint_y=None, height=200)
        img.bind(on_touch_down=self.show_image_editor)  # Bind click event to show_image_editor
        self.gallery_grid.add_widget(img)

    def add_resolution_control(self):
        # Add a button to change the camera resolution
        self.resolution_btn = Button(text='Resolution: 640x480', size_hint=(1, 0.1))
        self.resolution_btn.bind(on_press=self.change_resolution)
        self.camera_layout.add_widget(self.resolution_btn)

    def change_resolution(self, instance):
        # Change the camera resolution
        if self.cap and self.cap.isOpened():
            if self.resolution_btn.text == 'Resolution: 640x480':
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.resolution_btn.text = 'Resolution: 1280x720'
            else:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.resolution_btn.text = 'Resolution: 640x480'

    def add_flash_control(self):
        # Add a button to toggle flash (simulated)
        self.flash_btn = Button(text='Flash: Off', size_hint=(1, 0.1))
        self.flash_btn.bind(on_press=self.toggle_flash)
        self.camera_layout.add_widget(self.flash_btn)

    def toggle_flash(self, instance):
        # Toggle flash (simulated by adjusting brightness)
        if self.flash_btn.text == 'Flash: Off':
            self.flash_btn.text = 'Flash: On'
            self.adjust_brightness(None, 2.0)  # Max brightness
        else:
            self.flash_btn.text = 'Flash: Off'
            self.adjust_brightness(None, 1.0)  # Normal brightness

    def add_zoom_control(self):
        # Add a slider to control zoom (simulated by cropping)
        self.zoom_slider = Slider(min=1.0, max=3.0, value=1.0, size_hint=(1, 0.1))
        self.zoom_slider.bind(value=self.adjust_zoom)
        self.camera_layout.add_widget(self.zoom_slider)

    def adjust_zoom(self, instance, value):
        # Simulate zoom by cropping the frame
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                h, w = frame.shape[:2]
                zoom_factor = int(min(h, w) / value)
                cropped = frame[h//2 - zoom_factor//2:h//2 + zoom_factor//2,
                                w//2 - zoom_factor//2:w//2 + zoom_factor//2]
                resized = cv2.resize(cropped, (w, h))
                buf = resized.tobytes()
                texture = Texture.create(size=(w, h), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.camera_img.texture = texture

    def add_timer_control(self):
        # Add a button to enable a capture timer
        self.timer_btn = Button(text='Timer: Off', size_hint=(1, 0.1))
        self.timer_btn.bind(on_press=self.toggle_timer)
        self.camera_layout.add_widget(self.timer_btn)

    def toggle_timer(self, instance):
        # Toggle timer for capturing photos
        if self.timer_btn.text == 'Timer: Off':
            self.timer_btn.text = 'Timer: 3s'
            Clock.schedule_once(self.capture, 3)  # Capture after 3 seconds
        else:
            self.timer_btn.text = 'Timer: Off'

    def add_filter_controls(self):
        # Add a button to apply filters
        self.filter_btn = Button(text='Apply Filter', size_hint=(1, 0.1))
        self.filter_btn.bind(on_press=self.apply_filter)
        self.camera_layout.add_widget(self.filter_btn)

    def apply_filter(self, instance):
        # Apply a grayscale filter to the camera feed
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                filtered_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                buf = filtered_frame.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='luminance')
                texture.blit_buffer(buf, colorfmt='luminance', bufferfmt='ubyte')
                self.camera_img.texture = texture

    # Rest of the code remains the same...
        
    def update(self, dt=0):
        # Update camera feed only if camera is initialized
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 0)
                buf = frame.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.camera_img.texture = texture
            self.camera_img.canvas.ask_update()
            Clock.schedule_once(self.update, 1.0 / 30.0)  # Schedule the next update
    
    def capture(self, instance):
        # Capture an image from the camera only if camera is initialized
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Save the captured image
                if not os.path.exists('captured_images'):
                    os.makedirs('captured_images')
                image_path = f'captured_images/capture_{len(os.listdir("captured_images")) + 1}.png'
                cv2.imwrite(image_path, frame)
                print(f"Image Captured and saved to {image_path}")
                
                # Update the gallery
                self.update_gallery(image_path)
        else:
            print("Error: Camera is not initialized.")
    
    def show_image_editor(self):
        self.editor_layout = FloatLayout()
        self.editor_img = Image(source=self.selected_image_path, size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.6})
        self.editor_layout.add_widget(self.editor_img)
        self.crop_btn = Button(text='Crop', size_hint=(0.2, 0.1), pos_hint={'x': 0.1, 'y': 0.1})
        self.crop_btn.bind(on_press=self.crop_image)
        self.editor_layout.add_widget(self.crop_btn)
        self.brightness_slider = Slider(min=0.1, max=2.0, value=1.0, size_hint=(0.8, 0.1), pos_hint={'x': 0.1, 'y': 0.2})
        self.brightness_slider.bind(value=self.adjust_brightness)
        self.editor_layout.add_widget(self.brightness_slider)
        self.editor_popup = Popup(title="Edit Image", content=self.editor_layout, size_hint=(0.9, 0.9))
        self.editor_popup.open()
    
    def crop_image(self, instance):
        img = PILImage.open(self.selected_image_path)
        width, height = img.size
        cropped_img = img.crop((width // 4, height // 4, 3 * width // 4, 3 * height // 4))
        cropped_img.save(self.selected_image_path)
        self.editor_img.source = self.selected_image_path
        self.editor_img.reload()
    
    def adjust_brightness(self, instance, value):
        img = PILImage.open(self.selected_image_path)
        enhancer = ImageEnhance.Brightness(img)
        enhanced_img = enhancer.enhance(value)
        enhanced_img.save(self.selected_image_path)
        self.editor_img.source = self.selected_image_path
        self.editor_img.reload()
    
    def encrypt_message(self, instance):
        self.one_time_key = Fernet.generate_key()
        self.encrypt_popup = Popup(title="Encrypt Message", size_hint=(0.8, 0.4))
        self.encrypt_layout = BoxLayout(orientation='vertical')
        self.message_input = TextInput(hint_text='Enter secret message', size_hint=(1, 0.5))
        self.encrypt_layout.add_widget(self.message_input)
        self.copy_key_btn = Button(text='Copy One-Time Key', size_hint=(1, 0.25))
        self.copy_key_btn.bind(on_press=self.copy_key)
        self.encrypt_layout.add_widget(self.copy_key_btn)
        self.save_btn = Button(text='Save Encrypted Image', size_hint=(1, 0.25))
        self.save_btn.bind(on_press=self.save_encrypted_image)
        self.encrypt_layout.add_widget(self.save_btn)
        self.encrypt_popup.content = self.encrypt_layout
        self.encrypt_popup.open()
    
    def copy_key(self, instance):
        Clipboard.copy(self.one_time_key.decode())
        print("One-Time Key copied to clipboard!")
    
    def save_encrypted_image(self, instance):
        # Encrypt the message and save it in the image
        message = self.message_input.text
        if not message:
            print("Please enter a message!")
            return
        
        cipher = Fernet(self.one_time_key)
        encrypted_message = cipher.encrypt(message.encode())
        
        # Save the encrypted message in the image metadata
        img = PILImage.open(self.selected_image_path)
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("secret_message", encrypted_message.decode())
        
        # Save the image in PNG format
        encrypted_image_path = f'encrypted_{os.path.basename(self.selected_image_path)}'
        img.save(encrypted_image_path, "PNG", pnginfo=metadata)
        
        self.encrypt_popup.dismiss()
        print(f"Encrypted image saved to {encrypted_image_path}")
    
    def decrypt_message(self, instance):
        # Create the decryption popup
        self.decrypt_popup = Popup(title="Decrypt Message", size_hint=(0.8, 0.4))
        self.decrypt_layout = BoxLayout(orientation='vertical')
        
        # Add key input
        self.key_input = TextInput(hint_text='Enter One-Time Key', size_hint=(1, 0.5))
        self.decrypt_layout.add_widget(self.key_input)
        
        # Add decrypt button
        self.decrypt_confirm_btn = Button(text='Decrypt', size_hint=(1, 0.5))
        self.decrypt_confirm_btn.bind(on_press=self.confirm_decrypt)
        self.decrypt_layout.add_widget(self.decrypt_confirm_btn)
        
        # Open the popup
        self.decrypt_popup.content = self.decrypt_layout
        self.decrypt_popup.open()
    
    def confirm_decrypt(self, instance):
        # Decrypt the message
        key = self.key_input.text.encode()
        if not key:
            print("Please enter the one-time key!")
            return
        
        try:
            cipher = Fernet(key)
            img = PILImage.open(self.selected_image_path)
            encrypted_message = img.info.get("secret_message")
            if not encrypted_message:
                print("No encrypted message found in the image!")
                return
            
            decrypted_message = cipher.decrypt(encrypted_message.encode()).decode()
            print(f"Decrypted Message: {decrypted_message}")
            self.show_decrypted_message(decrypted_message)
        except Exception as e:
            print(f"Decryption failed: {e}")
    
    def show_decrypted_message(self, message):
        self.message_popup = Popup(title="Decrypted Message", size_hint=(0.8, 0.4))
        self.message_layout = BoxLayout(orientation='vertical')
        
        self.message_label = Label(text=message, size_hint=(1, 0.8))
        self.message_layout.add_widget(self.message_label)
        
        self.close_btn = Button(text='Close', size_hint=(1, 0.2))
        self.close_btn.bind(on_press=self.message_popup.dismiss)
        self.message_layout.add_widget(self.close_btn)
        
        self.message_popup.content = self.message_layout
        self.message_popup.open()
    def on_key_down(self, window, key, *args):
        print(f"Key pressed: {key}") 

        if key == 292: 
            self.select_image()
        elif key == 293:  
            self.select_image2()
    
    def select_image(self):
        print("Opening file chooser...")  
        self.file_chooser_layout = BoxLayout(orientation='vertical')

        self.file_chooser = FileChooserIconView(path=os.path.expanduser('~'))
        self.file_chooser_layout.add_widget(self.file_chooser)

        self.select_btn = Button(text='Select', size_hint=(1, 0.1))
        self.select_btn.bind(on_press=self.confirm_selection)
        self.file_chooser_layout.add_widget(self.select_btn)
        self.file_popup = Popup(title="Select Image", content=self.file_chooser_layout, size_hint=(0.9, 0.9))
        self.file_popup.open()

    def confirm_selection(self, instance):
        selection = self.file_chooser.selection
        if selection:
            self.selected_image_path = selection[0]
            print(f"Selected image: {self.selected_image_path}") 
            self.file_popup.dismiss()
            self.encrypt_message()
        else:
            print("No image selected!")
    
    def select_image2(self):
        print("Opening file chooser...")  

        self.file_chooser_layout = BoxLayout(orientation='vertical')

        self.file_chooser = FileChooserIconView(path=os.path.expanduser('~'))
        self.file_chooser_layout.add_widget(self.file_chooser)

        self.select_btn = Button(text='Select', size_hint=(1, 0.1))
        self.select_btn.bind(on_press=self.confirm_selection2)
        self.file_chooser_layout.add_widget(self.select_btn)
        self.file_popup = Popup(title="Select Image", content=self.file_chooser_layout, size_hint=(0.9, 0.9))
        self.file_popup.open()

    def confirm_selection2(self, instance):
        selection = self.file_chooser.selection
        if selection:
            self.selected_image_path = selection[0]
            print(f"Selected image: {self.selected_image_path}")
            self.file_popup.dismiss()
            self.decrypt_message()
        else:
            print("No image selected!")
    
    def encrypt_message(self):
        if not self.selected_image_path:
            print("No image selected!")
            return

        self.one_time_key = Fernet.generate_key()
        
        self.encrypt_popup = Popup(title="Encrypt Message", size_hint=(0.8, 0.4))
        self.encrypt_layout = BoxLayout(orientation='vertical')
        
        self.message_input = TextInput(hint_text='Enter secret message', size_hint=(1, 0.5))
        self.encrypt_layout.add_widget(self.message_input)
        
        self.encrypt_btn = Button(text='Encrypt', size_hint=(1, 0.25))
        self.encrypt_btn.bind(on_press=self.save_encrypted_image)
        self.encrypt_layout.add_widget(self.encrypt_btn)
        
        self.encrypt_popup.content = self.encrypt_layout
        self.encrypt_popup.open()
    
    import base64

    def save_encrypted_image(self, instance):
        message = self.message_input.text
        if not message:
            print("Please enter a message!")
            return

        cipher = Fernet(self.one_time_key)
        encrypted_message = cipher.encrypt(message.encode())
        encrypted_b64 = base64.b64encode(encrypted_message).decode()

        img = PILImage.open(self.selected_image_path)
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("secret_message", encrypted_b64)

        encrypted_image_path = f'encrypted_{os.path.basename(self.selected_image_path)}'
        img.save(encrypted_image_path, "PNG", pnginfo=metadata)

        Clipboard.copy(self.one_time_key.decode())  
        print("One-Time Key copied to clipboard!")
        self.encrypt_popup.dismiss()
        print(f"Encrypted image saved to {encrypted_image_path}")

    
    def decrypt_message(self):
        self.decrypt_popup = Popup(title="Decrypt Message", size_hint=(0.8, 0.4))
        self.decrypt_layout = BoxLayout(orientation='vertical')
        
        self.key_input = TextInput(hint_text='Enter One-Time Key', size_hint=(1, 0.5))
        self.decrypt_layout.add_widget(self.key_input)
        
        self.decrypt_btn = Button(text='Decrypt', size_hint=(1, 0.5))
        self.decrypt_btn.bind(on_press=self.confirm_decrypt)
        self.decrypt_layout.add_widget(self.decrypt_btn)
        
        self.decrypt_popup.content = self.decrypt_layout
        self.decrypt_popup.open()
    
    def confirm_decrypt(self, instance):
        key = self.key_input.text.encode()
        if not key:
            print("Please enter the one-time key!")
            return

        try:
            cipher = Fernet(key)
            img = PILImage.open(self.selected_image_path)
            encrypted_b64 = img.info.get("secret_message")
            
            if not encrypted_b64:
                print("No encrypted message found in the image!")
                return
            encrypted_message = base64.b64decode(encrypted_b64)

            decrypted_message = cipher.decrypt(encrypted_message).decode()
            print(f"Decrypted Message: {decrypted_message}")
            self.show_decrypted_message(decrypted_message)
        except Exception as e:
            print(f"Decryption failed: {e}")

    
    def show_decrypted_message(self, message):
        self.message_popup = Popup(title="Decrypted Message", size_hint=(0.8, 0.4))
        self.message_layout = BoxLayout(orientation='vertical')
        
        self.message_label = Label(text=message, size_hint=(1, 0.8))
        self.message_layout.add_widget(self.message_label)
        
        self.close_btn = Button(text='Close', size_hint=(1, 0.2))
        self.close_btn.bind(on_press=self.message_popup.dismiss)
        self.message_layout.add_widget(self.close_btn)
        
        self.message_popup.content = self.message_layout
        self.message_popup.open()


if __name__ == '__main__':
    CameraApp().run()