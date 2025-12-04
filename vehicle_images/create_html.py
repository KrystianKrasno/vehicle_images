import os

root = r"C:\Users\krasnok\OneDrive - TMNA\Desktop\CY2025"   # adjust to your local path
out_html = "vehicle_images/index.html"

html_head = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Vehicle Images Gallery</title>
  <style>
    body { font-family: sans-serif; }
    .gallery { display: flex; flex-wrap: wrap; gap: 16px; }
    .gallery img { max-width: 300px; height: auto; }
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
            rel = os.path.relpath(os.path.join(dirpath, fn), os.path.dirname(out_html))
            imgs.append(rel.replace(os.sep, '/'))

with open(out_html, "w", encoding="utf-8") as f:
    f.write(html_head)
    for img in imgs:
        f.write(f'    <img src="vehicle_images/{img}"\n')
    f.write(html_tail)

print(f"Wrote {len(imgs)} images into {out_html}")
