from flask import Flask, render_template, request, url_for, redirect
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load BLIP processor and model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption(image_path):
    """
    Generate a caption for the given image using BLIP.
    
    Args:
    - image_path (str): Path to the image file.
    
    Returns:
    - str: Generated caption for the image.
    """
    # Open the image using PIL
    image = Image.open(image_path).convert("RGB")
    
    # Preprocess the image and prepare inputs for the BLIP model
    inputs = processor(images=image, return_tensors="pt")
    
    # Generate caption using the model
    outputs = model.generate(**inputs)
    
    # Decode the output tokens into a readable string
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    return caption

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if an image is uploaded
        if "image" not in request.files:
            return "No file part"
        file = request.files["image"]
        if file.filename == "":
            return "No selected file"
        if file:
            # Save the uploaded image
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(image_path)
            
            # Generate a caption for the image
            caption = generate_caption(image_path)
            
            # Serve the result
            return render_template(
                "index.html",
                caption=caption,
                file_name=file.filename,  # Pass the file name to the template
                img_url=url_for("static", filename=f"uploads/{file.filename}")
            )
    return render_template("index.html")

@app.route("/logout")
def logout():
    # Redirect to the application running on port 5000
    return redirect("http://127.0.0.1:5000/")

if __name__ == "__main__":
    app.run(debug=True, port=7860)
