import cv2
import requests
import numpy as np
import threading
import time
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import quote

# -----------------------------
# USER SETTINGS
# -----------------------------

MONITOR_WIDTH = 480     # change to your monitor width
MONITOR_HEIGHT = 800    # change to your monitor height
DISPLAY_TIME = 10       # seconds per image
BUFFER_SIZE = 5         # number of images to preload
IMAGE_ROTATION = 0   # allowed values: 0, 90, 180, 270

SEARCH_TERM = "flower"


# -----------------------------
# Get image URLs from Google
# -----------------------------
def fetch_flower_image_urls(search_term, max_results=20):
    """
    Scrape Google Images search results and return image URLs.
    """
    query = quote(search_term)
    url = f"https://www.google.com/search?q={query}&tbm=isch"

    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    image_urls = []

    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src.startswith("http"):
            image_urls.append(src)

        if len(image_urls) >= max_results:
            break

    return image_urls


# -----------------------------
# Download image from URL
# -----------------------------
def download_image(url):
    """
    Download an image and convert it to OpenCV format.
    """
    try:
        response = requests.get(url, timeout=5)
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return image
    except:
        return None


# -----------------------------
# Crop image to match monitor aspect ratio
# -----------------------------
def crop_to_monitor_aspect(image, target_width, target_height):
    """
    Crop the center of the image to match the monitor aspect ratio.
    """
    h, w = image.shape[:2]

    target_ratio = target_width / target_height
    image_ratio = w / h

    if image_ratio > target_ratio:
        # Image too wide → crop sides
        new_width = int(h * target_ratio)
        start_x = (w - new_width) // 2
        cropped = image[:, start_x:start_x + new_width]
    else:
        # Image too tall → crop top/bottom
        new_height = int(w / target_ratio)
        start_y = (h - new_height) // 2
        cropped = image[start_y:start_y + new_height, :]

    return cropped


# -----------------------------
# Resize image to monitor size
# -----------------------------
def resize_to_monitor(image, width, height):
    """
    Resize image exactly to the monitor resolution.
    """
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

def rotate_image(image, rotation):
    """
    Rotate image by 0, 90, 180, or 270 degrees.
    """

    if rotation == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    if rotation == 180:
        return cv2.rotate(image, cv2.ROTATE_180)

    if rotation == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    return image


# -----------------------------
# Prepare image (download + crop + resize)
# -----------------------------
def prepare_image(url):
    """
    Download an image, only use it if it's at least as large as the monitor,
    then crop and resize to exactly MONITOR_WIDTH x MONITOR_HEIGHT.
    """
    image = download_image(url)
    if image is None:
        return None

    h, w = image.shape[:2]

    # Only accept images at least as large as the monitor
    if w < MONITOR_WIDTH or h < MONITOR_HEIGHT:
        return None

    # Crop to monitor aspect ratio and resize
    image = crop_to_monitor_aspect(image, MONITOR_WIDTH, MONITOR_HEIGHT)
    image = resize_to_monitor(image, MONITOR_WIDTH, MONITOR_HEIGHT)

    return image

# -----------------------------
# Fill image buffer in background
# -----------------------------
def buffer_loader(image_urls, buffer):
    """
    Continuously load images into the buffer so they are ready for display.
    """
    index = 0

    while True:
        if len(buffer) < BUFFER_SIZE:

            url = image_urls[index % len(image_urls)]
            index += 1

            image = prepare_image(url)

            if image is not None:
                buffer.append(image)

        else:
            time.sleep(0.5)


# -----------------------------
# Display images using OpenCV
# -----------------------------
def display_images(buffer):
    """
    Display images from buffer for DISPLAY_TIME seconds each.
    """
    cv2.namedWindow("Flowers", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Flowers", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:

        if len(buffer) > 0:
            image = buffer.popleft()

            cv2.imshow("Flowers", image)
            cv2.waitKey(1)

            start = time.time()

            # Keep image visible for DISPLAY_TIME seconds
            while time.time() - start < DISPLAY_TIME:
                cv2.waitKey(1)

        else:
            time.sleep(0.1)


# -----------------------------
# Main program
# -----------------------------
def main():

    print("Fetching flower image URLs...")
    image_urls = fetch_flower_image_urls(SEARCH_TERM)

    print("Found", len(image_urls), "images")

    image_buffer = deque()

    # Start background loader thread
    loader_thread = threading.Thread(
        target=buffer_loader,
        args=(image_urls, image_buffer),
        daemon=True
    )
    loader_thread.start()

    # Display images
    display_images(image_buffer)


if __name__ == "__main__":
    main()