import os

root = r"C:\Users\krasnok\OneDrive - TMNA\Desktop\CY2025\vehicle_images" 
out_html = os.path.join(root, "index.html") # Generate index.html right in the root folder

html_head = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Vehicle Images Gallery</title>
    <style>
        body { font-family: sans-serif; }
        .gallery { display: flex; flex-wrap: wrap; gap: 16px; }
        /* Adjusted max-width for better display */
        .gallery img { max-width: 300px; height: auto; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>Vehicle Images Gallery</h1>
    <div class="gallery">
"""

html_tail = """
    </div>
</body>
</html>
"""

imgs = []
for dirpath, _, filenames in os.walk(root):
    for fn in filenames:
        if fn.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            # 2. ***FIXED PATH CALCULATION***
            # Calculate the path relative to the 'root' directory (vehicle_images/).
            # This correctly yields 'images/filename.png'
            rel = os.path.relpath(os.path.join(dirpath, fn), root)
            imgs.append(rel.replace(os.sep, '/')) # Use forward slashes for URLs

with open(out_html, "w", encoding="utf-8") as f:
    f.write(html_head)
    for img in imgs:
        # Create a clean alt text from the filename
        alt_text = os.path.splitext(os.path.basename(img))[0]
        
        # 3. ***FIXED HTML GENERATION***
        # The path 'images/filename.png' is used directly, and the <img> tag is closed properly.
        f.write(f'        <img src="{img}" alt="{alt_text}" title="{alt_text}">\n')
    f.write(html_tail)

print(f"Wrote {len(imgs)} images into {out_html}")