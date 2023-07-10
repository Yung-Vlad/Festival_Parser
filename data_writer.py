import csv
from PIL import Image
import json
import img2pdf

# write our collected info to json
def write_to_json(full_info):
    # write info to json
    with open("data/cards-info.json", 'w', encoding="utf-8") as file:
        json.dump(full_info, file, indent=4, ensure_ascii=False)


# write our collected info to csv
def write_to_csv(full_info):
    with open("data/cards-info.csv", 'w', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                "Name",
                "Place",
                "Date",
                "Link",
                "Rating",
                "Tags",
                "Musicians"
            )
        )

    for i in full_info:
        with open("data/cards-info.csv", 'a', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    i["Name"],
                    i["Place"],
                    i["Date"],
                    i["Link"],
                    i["Rating"],
                    i["Tags"],
                    i["Musicians"]
                )
            )


# convert images to pdf
def convert_to_pdf(images_list):
    # convert to RGB mode and removing the alpha channel
    for image_path in images_list:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img.save(image_path)

    with open("data/fest-covers.pdf", "wb") as file:
        file.write(img2pdf.convert(images_list))