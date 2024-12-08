from PIL import Image
import os


def process_images(input_dir, output_dir, size=(400, 400)):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nr = 1

    for filename in os.listdir(input_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(input_dir, filename)
            with Image.open(filepath) as img:
                # Bildgröße anpassen, um genau auf die Zielgröße zu skalieren
                img_resized = img.resize(size, Image.LANCZOS)

                # In das PNG-Format konvertieren und speichern
                output_filename = f"sport_{nr}.png"
                output_filepath = os.path.join(output_dir, output_filename)
                img_resized.save(output_filepath, 'PNG')
                nr += 1
                print(f"Processed: {output_filepath}")


# Beispielverwendung
input_directory = "pics/convert"
output_directory = "pics/Sport"
process_images(input_directory, output_directory)
print("Finished")
