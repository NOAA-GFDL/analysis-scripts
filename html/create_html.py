import os
from datetime import datetime  # Import datetime module


def create_image_gallery_html(directory_path, output_filename="figures.html"):
   """
   Generates an HTML file to display images from a given directory.


   Args:
       directory_path (str): The path to the directory containing the image files.
       output_filename (str): The name of the HTML file to be created (default: figures.html).
   """
   image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
   image_files = []


   try:
       files = os.listdir(directory_path)
       for file in files:
           if any(file.lower().endswith(ext) for ext in image_extensions):
               image_files.append(file)
   except FileNotFoundError:
       print(f"Error: Directory not found at '{directory_path}'")
       return


   if not image_files:
       print(f"No image files found in '{directory_path}' with extensions: {', '.join(image_extensions)}")
       return


   html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>Analysis Figures</title>
   <style>
       body {{ font-family: sans-serif; }}
       .gallery {{ display: flex; flex-direction: column; gap: 10px; }}
       .gallery img {{ border: 1px solid #ccc; padding: 5px; box-sizing: border-box; }}
   </style>
</head>
<body>
   <h1>Analysis Figures</h1>
   <p>Figures shown from directory: {directory_path}</p>
   <p>File generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
   <div class="gallery">
   """


   for image_file in image_files:
       image_path = os.path.join(directory_path, image_file)
       html_content += f'        <img src="{image_path}" alt="{os.path.splitext(image_file)[0]}">\n'
   html_content += """
   </div>
</body>
</html>
   """

   try:
       with open(output_filename, 'w') as f:
           f.write(html_content)
       print(f"HTML file '{output_filename}' created successfully in the specified directory.")
   except Exception as e:
       print(f"Error writing to file '{output_filename}': {e}")

# Example Usage

create_image_gallery_html(r"/home/Anthony.Preucil/work_a2p/code/plots", r"/home/Anthony.Preucil/work_a2p/code/plots/figures.html")