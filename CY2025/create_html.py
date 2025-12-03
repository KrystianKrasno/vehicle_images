import os

# Define the folder containing your PNG files
# Use '.' to signify the current directory where the script is run
image_folder = r'C:\Users\krasnok\OneDrive - TMNA\Desktop\CY2025\CY2025' 

# The HTML template for each file
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{image_title}</title>
    <style>
        /* Simple styling to center the image */
        body {{ 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            margin: 0; 
            background-color: #f0f0f0; 
        }}
        img {{ 
            max-width: 100%; 
            height: auto; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <img src="{image_filename}" alt="{image_title}">
</body>
</html>
"""

# Iterate over all files in the current directory
for filename in os.listdir(image_folder):
    if filename.endswith(".png"):
        # 1. Create the new HTML filename (e.g., image.png -> image.html)
        html_filename = os.path.splitext(filename)[0] + ".html"
        
        # 2. Get the title (image name without extension)
        image_title = os.path.splitext(filename)[0]
        
        # 3. Format the HTML content
        html_content = html_template.format(
            image_filename=filename, 
            image_title=image_title
        )
        
        # 4. Write the content to the new HTML file
        with open(html_filename, "w") as f:
            f.write(html_content)

print("Conversion complete! HTML files created for all PNGs.")