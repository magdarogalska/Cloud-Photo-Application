from PIL import ImageFilter, ImageOps


def sepia_filter(image):
    # Implement the sepia filter and return the filtered image
    # Example code to apply a simple sepia filter (you can find more advanced methods online):
    sepia = image.convert("RGB")
    sepia = sepia.filter(ImageFilter.Color3DLUT([...]))  # Define a proper 3D LUT
    return sepia

def poster_filter(image):
    # Implement the posterize filter and return the filtered image
    # Example code to apply a simple posterize filter:
    posterize = ImageOps.posterize(image, 4)  # Number of colors (adjust as needed)
    return posterize