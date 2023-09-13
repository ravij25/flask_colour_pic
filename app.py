from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import cv2
import numpy as np

app = Flask(__name__)

# Create an "uploads" folder if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and "photo" in request.files:
        photo = request.files["photo"]
        if photo:
            # Save the uploaded photo to the "uploads" folder
            photo_path = os.path.join("uploads", photo.filename)
            photo.save(photo_path)

            # Check if the "enhance" checkbox is selected
            enhance = request.form.get("enhance") == "on"

            # Get the list of color adjustments from the form
            color_adjustments = []
            num_color_fields = len(request.form.getlist("color"))
            for i in range(num_color_fields):
                color_str = request.form.getlist("color")[i]
                strength = int(request.form.getlist("strength")[i])
                color = eval(color_str)
                color_adjustments.append((color, strength))

            # Modify the image based on the color adjustments
            modified_photo_path = os.path.join("uploads", "modified_" + photo.filename)
            apply_color_adjustments(photo_path, modified_photo_path, color_adjustments)

            # Enhance the image if selected
            if enhance:
                enhanced_photo_path = os.path.join("uploads", "enhanced_" + photo.filename)
                enhance_image(modified_photo_path, enhanced_photo_path)
                return render_template("index.html", photo_path=photo.filename, modified_photo_path="modified_" + photo.filename, enhanced_photo_path="enhanced_" + photo.filename)

            return render_template("index.html", photo_path=photo.filename, modified_photo_path="modified_" + photo.filename, enhanced_photo_path=None)

    return render_template("index.html", photo_path=None, modified_photo_path=None, enhanced_photo_path=None)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# Function to apply multiple color adjustments to the image
def apply_color_adjustments(input_path, output_path, color_adjustments):
    image = cv2.imread(input_path)

    if image is not None:
        # Convert the image to float32 for accurate calculations
        image = image.astype(np.float32)

        for color, strength in color_adjustments:
            # Apply color adjustment to each pixel with the specified strength
            image += np.array(color, dtype=np.float32) * strength / 100

        # Ensure pixel values are within the valid range (0-255)
        image = np.clip(image, 0, 255).astype(np.uint8)

        # Save the modified image
        cv2.imwrite(output_path, image)
    else:
        raise Exception("Failed to load the image")

# Function to enhance the image
def enhance_image(input_path, output_path):
    image = cv2.imread(input_path)

    if image is not None:
        # Apply basic image enhancement (e.g., denoising and upscaling)
        enhanced_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        enhanced_image = cv2.resize(enhanced_image, (image.shape[1] * 2, image.shape[0] * 2))

        # Save the enhanced image
        cv2.imwrite(output_path, enhanced_image)
    else:
        raise Exception("Failed to load the image")

if __name__ == "__main__":
    app.run(debug=True)
