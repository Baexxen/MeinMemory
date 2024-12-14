from PIL import Image
import os


def process_images(input_dir, output_dir, max_size=(400, 400)):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nr = 1

    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            with Image.open(filepath) as img:
                # Bildgröße proportional anpassen
                img.thumbnail(max_size, Image.LANCZOS)

                # In das PNG-Format konvertieren und speichern
                output_filename = f"e_l_{nr}.png"
                output_filepath = os.path.join(output_dir, output_filename)
                img.save(output_filepath, 'PNG')
                nr += 1
                print(f"Processed: {output_filepath}")
        else:
            if os.path.exists(filepath):
                print(f"removing {filepath}")
                os.remove(filepath)
        if os.path.exists(filepath):
            print(f"removing {filepath}")
            os.remove(filepath)


# Beispielverwendung
input_directory = "pics/convert"
output_directory = "pics/EigeneLandschaften"
process_images(input_directory, output_directory)
print("Finished")
