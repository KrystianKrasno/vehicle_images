import os

# Define the folder containing your PNG files
image_folder = r'C:\Users\krasnok\OneDrive - TMNA\Desktop\CY2025\vehicle_images\images' 

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
    </style>py
</head>
<body>
    <img src="vehicle_images/images/{image_filename}" alt="{image_title}">
</body>
</html>
"""

# Iterate over all files in the current directory
for filename in os.listdir(image_folder):
    # Only process PNG files that start with "2025"
    if filename.endswith(".png") and filename.startswith("2025"):
        
        # 1. Get the base name (e.g., "2025 Grand Highlander")
        base_name = os.path.splitext(filename)[0]
        
        # 2. Drop the "2025" and leading space 
        #    (Assuming the name is always "2025 XXXXX" or "2025 XXXXX.png")
        #    Slicing from index 5 effectively removes the first 5 characters ("2025 ")
        cleaned_name = base_name[5:]
        
        # 3. Replace spaces with underscores for the HTML filename
        html_file_name_base = cleaned_name.replace(" ", "_")
        
        # 4. Create the final HTML filename (e.g., Grand_Highlander.html)
        html_filename = html_file_name_base + ".html"
        
        # 5. Format the HTML content
        #    Use the cleaned name as the title
        html_content = html_template.format(
            image_filename=filename,  # Keep the original PNG name for the src attribute
            image_title=cleaned_name
        )
        
        # 6. Write the content to the new HTML file
        with open(html_filename, "w") as f:
            f.write(html_content)

print("Conversion complete! HTML files created with cleaned names.")