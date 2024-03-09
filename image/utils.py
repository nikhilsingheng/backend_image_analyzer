from datetime import datetime, timezone
from PIL import Image  
from io import BytesIO
import csv
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from io import StringIO
from reportlab.pdfgen import canvas
import os
from PIL.ExifTags import TAGS
from reportlab.lib import colors
from datetime import datetime
def get_image_metadata(image):
    
 
    img = Image.open(image)
    height_meters = img.height * 0.0254  
    speed_meters_per_second = 6
    return {
        'height': height_meters,
        'speed': speed_meters_per_second
    }

def calculate_speed(image):
    distance = 60 
    time_taken = image.created_at.replace(tzinfo=timezone.utc)  
    current_time = datetime.now(timezone.utc)
    time_diff = (current_time - time_taken).total_seconds()
    if time_diff > 0:
        speed = distance / time_diff
    else:
        speed = None
    
    return speed

def analyze_exif_data(uploaded_image):
    speed = calculate_speed(uploaded_image)
    if speed is not None:
        uploaded_image.speed = speed
        uploaded_image.save()
        
        print(f"Speed: {speed} meters per second")
        if speed > 5:
            uploaded_image.speed_flag = True
            uploaded_image.save()
    else:
        print("Error: Unable to calculate speed. Time difference is not positive.")
  
    try:
        image_path = uploaded_image.image.path
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag)
                    print(f"Tag: {tag}, Tag Name: {tag_name}, Value: {value}")
                    if tag_name == 'ExifImageWidth':
                        uploaded_image.width = value
                    elif tag_name == 'ExifImageHeight':
                        uploaded_image.height = value
                        if  uploaded_image.height > 60:
                             uploaded_image.image_height_flag = True
                             uploaded_image.save()
                    elif tag_name == 'DateTime':
                        uploaded_image.created_at = value
                        uploaded_image.updated_at = value
                uploaded_image.megapixels = (uploaded_image.width * uploaded_image.height) / 1000000
                uploaded_image.save()
    except Exception as e:
        print(f"Error analyzing EXIF data: {e}")





def generate_csv_report(images, folder_path='media/csv/', file_name='report.csv'):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path, file_name)

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Image', 'Height', 'Width','Image Size', 'Speed', 'Speed_Flag','Image_Height_Flag','Analyzed', 'Analyzed at'])
    for image in images:
        image_url = image.get('image', 'N/A')
        height = image.get('height', 'N/A')
        width = image.get('width', 'N/A')
        if height is not None and width is not None:
            try:
                image_size = f"{width}x{height}"
            except ValueError:
                image_size = 'N/A'
        else:
            image_size = 'N/A'
        speed = image.get('speed', 'N/A')
        speed_flag= image.get('speed_flag', 'N/A')
        image_height_flag=image.get('image_height_flag', 'N/A')
        analyzed = image.get('analyzed', 'N/A')
        analyzed_at = image.get('updated_at', 'N/A')
        writer.writerow([image_url, height, width,image_size, speed, speed_flag, image_height_flag, analyzed , analyzed_at])

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write(buffer.getvalue())

    return file_path



def generate_pdf_report(images):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica", 12)
    y_position = 750

    for image_data in images:
        if y_position < 200:
            p.showPage()
            p.setFont("Helvetica", 12)
            y_position = 750

  
        p.setFillColor(colors.blue) 
        p.drawString(100, y_position, "Analysis Report")
        y_position -= 20
        p.setFillColor(colors.black)  

 
        try:
            image_url = image_data['image']
        except (UnicodeDecodeError, AttributeError):
            image_url = str(image_data['image'])
        p.drawString(100, y_position, f"Image: {image_url}")
        y_position -= 20

        p.drawString(100, y_position, f"Height: {image_data['height']}")
        y_position -= 20

        p.drawString(100, y_position, f"Width: {image_data['width']}")
        y_position -= 20

        image_size = f"{image_data['width']}x{image_data['height']}"
        p.drawString(100, y_position, f"Image Size: {image_size}")
        y_position -= 20

        p.drawString(100, y_position, f"Speed: {image_data.get('speed', 'N/A')}")
        y_position -= 20

        p.drawString(100, y_position, f"Speed Flag: {image_data.get('speed_flag', 'N/A')}")
        y_position -= 20

        p.drawString(100, y_position, f"Image Height Flag: {image_data.get('image_height_flag', 'N/A')}")
        y_position -= 20

        p.drawString(100, y_position, f"Analyzed: {image_data.get('analyzed', 'N/A')}")
        y_position -= 20

        analyzed_at = image_data.get('updated_at', 'N/A')
        p.drawString(100, y_position, f"Analyzed at: {analyzed_at}")
        y_position -= 20

        p.setFillColor(colors.blue)
        p.drawString(100, y_position, "Additional Metadata:")
        p.setFillColor(colors.black)
        y_position -= 20

        for key, value in image_data.items():
            if key not in ['image', 'height', 'width', 'speed', 'speed_flag', 'image_height_flag', 'analyzed', 'updated_at']:
                if y_position < 200:
                    p.showPage()
                    p.setFont("Helvetica", 12)
                    y_position = 750

                p.drawString(120, y_position, f"{key.capitalize()}: {value}")
                y_position -= 20

        fig, ax = plt.subplots(figsize=(6, 3))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, color='blue')
        ax.set_title('Sample Graph', color='blue')
        ax.set_xlabel('X-axis', color='green')
        ax.set_ylabel('Y-axis', color='green')
        ax.grid(True)
        plt.tight_layout()
        plt.savefig("graph.png", format='png')
        plt.close(fig)
        p.drawImage("graph.png", 100, y_position - 180, width=400, height=200)
        y_position -= 220

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()
