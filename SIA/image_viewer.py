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
from PIL import Image as PILImage, ImageEnhance, PngImagePlugin, ImageOps
from kivy.core.window import Window
import base64
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFloatingActionButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar.toolbar import MDTopAppBar
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.theming import ThemeManager

class CameraApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"  # Set primary color
        self.theme_cls.accent_palette = "Orange"  # Set accent color
        self.title = 'Camera App'

        # Main layout
        self.tabs = TabbedPanel(do_default_tab=False)  # Disable default tab

        # Camera Tab
        self.camera_tab = TabbedPanelItem(text='Camera')
        self.camera_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Toolbar
        self.toolbar = MDTopAppBar(title="Camera App")  # Use MDTopAppBar
        self.toolbar.md_bg_color = self.theme_cls.primary_color
        self.toolbar.left_action_items = [["menu", lambda x: None]]  # Add a menu icon
        self.camera_layout.add_widget(self.toolbar)

        # Camera feed
        self.camera_img = Image()
        self.camera_layout.add_widget(self.camera_img)

        # Control buttons in a horizontal layout
        self.controls_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10, padding=10)

        # Flash button
        self.flash_btn = MDFloatingActionButton(
            icon="flash",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.accent_color,
        )
        self.flash_btn.bind(on_press=self.toggle_flash)
        self.controls_layout.add_widget(self.flash_btn)

        # Capture button
        self.capture_btn = MDFloatingActionButton(
            icon="camera",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.primary_color,
        )
        self.capture_btn.bind(on_press=self.capture)
        self.controls_layout.add_widget(self.capture_btn)

        # Filter button
        self.filter_btn = MDFloatingActionButton(
            icon="image-filter-black-white",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.accent_color,
        )
        self.filter_btn.bind(on_press=self.toggle_filter)
        self.controls_layout.add_widget(self.filter_btn)

        # Timer button
        self.timer_btn = MDFloatingActionButton(
            icon="timer",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.primary_color,
        )
        self.timer_btn.bind(on_press=self.toggle_timer)
        self.controls_layout.add_widget(self.timer_btn)

        self.camera_layout.add_widget(self.controls_layout)

        # Zoom slider
        self.zoom_slider = Slider(min=1.0, max=3.0, value=1.0, size_hint=(1, 0.1))
        self.zoom_slider.bind(value=self.adjust_zoom)
        self.camera_layout.add_widget(self.zoom_slider)

        self.camera_tab.add_widget(self.camera_layout)
        self.tabs.add_widget(self.camera_tab)

        # Gallery Tab
        self.gallery_tab = TabbedPanelItem(text='Gallery')
        self.gallery_layout = BoxLayout(orientation='vertical')

        # Add image button
        self.add_image_btn = MDRaisedButton(
            text='Choose Image from Device',
            size_hint=(1, 0.1),
            md_bg_color=self.theme_cls.primary_color,
        )
        self.add_image_btn.bind(on_press=self.open_file_chooser)
        self.gallery_layout.add_widget(self.add_image_btn)

        # Scrollable gallery
        self.scroll_view = ScrollView()
        self.gallery_grid = GridLayout(cols=3, size_hint_y=None, spacing=10, padding=10)
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
            Clock.schedule_interval(self.update, 1.0 / 30.0)  # Start the update loop

        Window.bind(on_key_down=self.on_key_down)
        self.selected_image_path = None
        self.flash_on = False  # Track flash state
        self.zoom_factor = 1.0  # Track zoom state
        self.filter_on = False  # Track filter state
        self.timer_on = False  # Track timer state

        return self.tabs

    def on_stop(self):
        # Release the camera when the app is closed
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def open_file_chooser(self, instance):
        # Create a file chooser popup
        self.file_chooser = FileChooserIconView()
        self.file_chooser.bind(on_selection=self.add_image_to_gallery)

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
        # Create a card for each image
        card = MDCard(size_hint=(None, None), size=(200, 250), elevation=10, padding=10, radius=[20])
        
        # Image inside the card
        img = Image(source=image_path, size_hint_y=None, height=150)
        img.bind(on_touch_down=self.show_image_editor)  # Click to edit
        
        # Add a label with filename
        label = MDLabel(text=os.path.basename(image_path), halign="center", theme_text_color="Secondary")

        # Delete button
        delete_btn = MDRaisedButton(text="Delete", size_hint=(1, None), md_bg_color=(1, 0, 0, 1))
        delete_btn.bind(on_press=lambda x: self.delete_image(image_path, card))

        # Arrange elements in card layout
        card.add_widget(img)
        card.add_widget(label)
        card.add_widget(delete_btn)

        self.gallery_grid.add_widget(card)
        self.gallery_grid.height = len(self.gallery_grid.children) * 250
    def toggle_flash(self, instance):
        # Toggle flash (simulated by adjusting brightness)
        if self.flash_btn.icon == "flash":
            self.flash_btn.icon = "flash-off"
            self.flash_on = True
        else:
            self.flash_btn.icon = "flash"
            self.flash_on = False

    def adjust_zoom(self, instance, value):
        self.zoom_factor = value

    def toggle_timer(self, instance):
        # Toggle timer for capturing photos
        if self.timer_btn.icon == "timer":
            self.timer_btn.icon = "timer-off"
            self.timer_on = True
            Clock.schedule_once(lambda dt: self.capture(instance), 3)  # Capture after 3 seconds
        else:
            self.timer_btn.icon = "timer"
            self.timer_on = False

    def toggle_filter(self, instance):
        # Toggle filter for the camera feed
        if self.filter_btn.icon == "image-filter-black-white":
            self.filter_btn.icon = "image-filter-center-focus"
            self.filter_on = True
        else:
            self.filter_btn.icon = "image-filter-black-white"
            self.filter_on = False

    def update(self, dt=0):
        if not self.cap or not self.cap.isOpened():
            print("Camera not initialized or failed to open.")
            return

        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame.")
            return

        h, w = frame.shape[:2]

        # Ensure zoom factor doesn't go out of bounds
        zoom_w = int(w / self.zoom_factor)
        zoom_h = int(h / self.zoom_factor)
        x1 = max(0, (w - zoom_w) // 2)
        y1 = max(0, (h - zoom_h) // 2)
        x2 = min(w, x1 + zoom_w)
        y2 = min(h, y1 + zoom_h)

        cropped = frame[y1:y2, x1:x2]  # Crop the zoomed area
        resized = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)  # Resize back

        # Apply flash effect
        if self.flash_on:
            resized = cv2.convertScaleAbs(resized, alpha=1.5, beta=50)

        # Apply filter
        if self.filter_on:
            resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)  # Convert back to BGR for display

        # Convert BGR to RGB and flip vertically
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        resized = cv2.flip(resized, 0)

        # Display the frame
        buf = resized.tobytes()
        texture = Texture.create(size=(w, h), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.camera_img.texture = texture

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
                # Update the gallery only if the image was successfully captured
                self.update_gallery(image_path)
            else:
                print("Error: Failed to capture image.")
        else:
            print("Error: Camera is not initialized.")

    def show_image_editor(self, image_path):
        """Opens the image editor with full functionality."""
        self.selected_image_path = image_path  # Set selected image

        # **Main Layout**
        self.editor_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # **Moderate-Sized Image Preview (Click to View Full)**
        self.image_card = MDCard(
            size_hint=(0.9, 0.55),  # Large but not fullscreen
            elevation=10,
            radius=[25], 
            padding=10,
            md_bg_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5}
        )
        self.editor_img = Image(
            source=self.selected_image_path, 
            size_hint=(1, 1),
            fit_mode="contain"  # Use fit_mode instead of allow_stretch and keep_ratio
        )

        # **Click Image to View Full**
        self.editor_img.bind(on_touch_down=self.show_full_image)

        self.image_card.add_widget(self.editor_img)
        self.editor_layout.add_widget(self.image_card)

        # **Adjustment Sliders (Brightness, Contrast, Hue, Saturation)**
        self.sliders_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # **Brightness**
        self.brightness_slider = Slider(min=0.1, max=2.0, value=1.0)
        self.brightness_slider.bind(value=self.adjust_brightness)
        self.sliders_layout.add_widget(MDLabel(text="Brightness", halign="center", theme_text_color="Secondary"))
        self.sliders_layout.add_widget(self.brightness_slider)

        # **Contrast**
        self.contrast_slider = Slider(min=0.1, max=2.0, value=1.0)
        self.contrast_slider.bind(value=self.adjust_contrast)
        self.sliders_layout.add_widget(MDLabel(text="Contrast", halign="center", theme_text_color="Secondary"))
        self.sliders_layout.add_widget(self.contrast_slider)

        # **Saturation**
        self.saturation_slider = Slider(min=0.1, max=2.0, value=1.0)
        self.saturation_slider.bind(value=self.adjust_saturation)
        self.sliders_layout.add_widget(MDLabel(text="Saturation", halign="center", theme_text_color="Secondary"))
        self.sliders_layout.add_widget(self.saturation_slider)

        # **Hue**
        self.hue_slider = Slider(min=0.5, max=1.5, value=1.0)
        self.hue_slider.bind(value=self.adjust_hue)
        self.sliders_layout.add_widget(MDLabel(text="Hue", halign="center", theme_text_color="Secondary"))
        self.sliders_layout.add_widget(self.hue_slider)

        self.editor_layout.add_widget(self.sliders_layout)

        # **Buttons Layout (Crop, Grayscale, Save, Close)**
        self.buttons_layout = BoxLayout(orientation="horizontal", spacing=15, padding=10, size_hint=(1, 0.15))

        # Crop Button
        self.crop_btn = MDRaisedButton(text="Crop", md_bg_color=(0.5, 0.3, 1, 1), size_hint=(0.3, None), height=50)
        self.crop_btn.bind(on_press=self.crop_image)
        self.buttons_layout.add_widget(self.crop_btn)

        # Grayscale Button
        self.gray_btn = MDRaisedButton(text="Grayscale", md_bg_color=(0.2, 0.2, 0.2, 1), size_hint=(0.3, None), height=50)
        self.gray_btn.bind(on_press=self.apply_grayscale)
        self.buttons_layout.add_widget(self.gray_btn)

        # Save Button
        self.save_btn = MDRaisedButton(text="Save", md_bg_color=(0, 0.5, 0, 1), size_hint=(0.3, None), height=50)
        self.save_btn.bind(on_press=self.save_edited_image)
        self.buttons_layout.add_widget(self.save_btn)

        # Close Button
        self.close_btn = MDRaisedButton(text="Close", md_bg_color=(1, 0, 0, 1), size_hint=(0.3, None), height=50)
        self.close_btn.bind(on_press=lambda x: self.editor_popup.dismiss())
        self.buttons_layout.add_widget(self.close_btn)

        self.editor_layout.add_widget(self.buttons_layout)

        # **Popup**
        self.editor_popup = Popup(title="Edit Image", content=self.editor_layout, size_hint=(1, 1))
        self.editor_popup.open()

    def on_touch_down(self, instance, touch):
        """Handles the touch event on the image to show the full image."""
        if instance.collide_point(*touch.pos):
            self.selected_image_path = instance.source  # Set the selected image path
            self.show_full_image(instance, touch) 

    def show_full_image(self, instance, touch):
        """Displays the full image when clicked."""
        if instance.collide_point(*touch.pos):
            full_image_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

            # Load the image using PIL to get its original dimensions
            img = PILImage.open(self.selected_image_path)
            width, height = img.size
            screen_width, screen_height = Window.size

            # Calculate the maximum width and height for the image to fit within the screen
            max_width = screen_width * 0.95  # 95% of screen width
            max_height = screen_height * 0.8  # 80% of screen height
            aspect_ratio = width / height

            # Resize the image to fit within the screen while maintaining aspect ratio
            if width > max_width:
                width = max_width
                height = width / aspect_ratio
            
            if height > max_height:
                height = max_height
                width = height * aspect_ratio

            # Create the image widget with the resized dimensions
            full_img = Image(
                source=self.selected_image_path,
                size_hint=(None, None),
                size=(width, height),
                fit_mode="contain"  # Use fit_mode instead of allow_stretch and keep_ratio
            )

            # Add the image to the layout
            full_image_layout.add_widget(full_img)

            # Close Button
            close_btn = MDRaisedButton(
                text="Close", 
                md_bg_color=(1, 0, 0, 1), 
                size_hint=(1, None), 
                height=50
            )
            close_btn.bind(on_press=lambda x: self.full_image_popup.dismiss())

            full_image_layout.add_widget(close_btn)

            # Popup with Full Image
            self.full_image_popup = Popup(
                title="Full Image", 
                content=full_image_layout, 
                size_hint=(1, 1)
            )
            self.full_image_popup.open()

    def crop_image(self, instance):
        img = PILImage.open(self.selected_image_path)
        width, height = img.size
        cropped_img = img.crop((width // 4, height // 4, 3 * width // 4, 3 * height // 4))
        cropped_img.save(self.selected_image_path)
        self.editor_img.source = self.selected_image_path
        self.editor_img.reload()

    def apply_grayscale(self, instance):
        """Convert the image to grayscale."""
        img = PILImage.open(self.selected_image_path).convert("L")  # Convert to grayscale
        img.save(self.selected_image_path)
        self.editor_img.source = self.selected_image_path
        self.editor_img.reload()

    def adjust_brightness(self, instance, value):
        img = PILImage.open(self.selected_image_path)
        enhancer = ImageEnhance.Brightness(img)
        enhanced_img = enhancer.enhance(value)
        enhanced_img.save(self.selected_image_path)
        self.editor_img.source = self.selected_image_path
        self.editor_img.reload()

    def adjust_contrast(self, instance, value):
        img = PILImage.open(self.selected_image_path)
        enhancer = ImageEnhance.Contrast(img)
        enhanced_img = enhancer.enhance(value)
        enhanced_img.save(self.selected_image_path)
        self.editor_img.source = self.selected_image_path
        self.editor_img.reload()

    def adjust_saturation(self, instance, value):
        img = PILImage.open(self.selected_image_path)
        enhancer = ImageEnhance.Color(img)
        enhanced_img = enhancer.enhance(value)
        enhanced_img.save(self.selected_image_path)
        self.editor_img.source = self.selected_image_path
        self.editor_img.reload()

    def adjust_hue(self, instance, value):
        img = PILImage.open(self.selected_image_path).convert("HSV")
        pixels = img.load()

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                h, s, v = pixels[i, j]
                h = int(h * value)  
                pixels[i, j] = (h, s, v)

        img = img.convert("RGB")
        img.save(self.selected_image_path)
        self.editor_img.source = self.selected_image_path
        self.editor_img.reload()


    def save_edited_image(self, instance):
        """Saves the edited image and refreshes the gallery."""
        if self.selected_image_path:
            print(f"Saving edited image: {self.selected_image_path}")

            # Ensure the edited image is saved
            self.editor_img.reload()

            # Close editor popup
            self.editor_popup.dismiss()

            # Refresh the gallery to reflect the edited image
            self.refresh_gallery()

    
    def refresh_gallery(self):
        """Clears and reloads the gallery with updated images."""
        self.gallery_grid.clear_widgets()  # Clear old images

        # Reload images from the 'captured_images' folder
        if os.path.exists("captured_images"):
            for image in sorted(os.listdir("captured_images")):
                image_path = os.path.join("captured_images", image)
                self.update_gallery(image_path)  # Re-add images to gallery



    def delete_image(self, image_path, card):
        """Delete image from gallery and remove it from storage."""
        if os.path.exists(image_path):
            os.remove(image_path)  # Delete the file
        self.gallery_grid.remove_widget(card)  # Remove from UI
        print(f"Deleted: {image_path}")

    def update_gallery(self, image_path):
        # Create an MDCard for each image
        card = MDCard(
            size_hint=(None, None), 
            size=(220, 280),  # Increased size for better layout
            elevation=10, 
            padding=10, 
            radius=[20],  # Rounded corners
            md_bg_color=(1, 1, 1, 1)
        )

        # Image inside the card
        img = Image(source=image_path, size_hint_y=None, height=150, fit_mode="contain")
        img.bind(on_touch_down=self.on_touch_down)  # Bind the on_touch_down event

        # Label with filename
        label = MDLabel(
            text=os.path.basename(image_path), 
            halign="center", 
            theme_text_color="Secondary", 
            size_hint_y=None,
            height=20
        )

        # **Edit Image Button**
        edit_btn = MDRaisedButton(
            text="Edit Image",
            size_hint=(1, None),
            md_bg_color=(0.2, 0.6, 0.8, 1)
        )
        edit_btn.bind(on_press=lambda x: self.show_image_editor(image_path))  # Open editor on click

        # **Delete Button**
        delete_btn = MDRaisedButton(
            text="Delete", 
            size_hint=(1, None), 
            md_bg_color=(1, 0, 0, 1)
        )
        delete_btn.bind(on_press=lambda x: self.delete_image(image_path, card))

        # Arrange elements in card layout
        card_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        card_layout.add_widget(img)
        card_layout.add_widget(label)
        card_layout.add_widget(edit_btn)  # Add Edit Button
        card_layout.add_widget(delete_btn)

        # Add layout to card
        card.add_widget(card_layout)

        # Add the card to the gallery grid
        self.gallery_grid.add_widget(card)
        self.gallery_grid.height = len(self.gallery_grid.children) * 280  # Adjust height dynamically

            
    def on_key_down(self, window, key, *args):
        if key == 116:
            self.toggle_timer(None)
        elif key == 292 or key==24: 
            self.select_image()
        elif key == 293 or key==23:  
            self.select_image2()
        else:
            print(f"Key code: {key}")
    
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
