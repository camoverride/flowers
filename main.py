import cv2
import requests
import numpy as np
import threading
import time
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import quote



MONITOR_WIDTH = 480     # change to your monitor width
MONITOR_HEIGHT = 800    # change to your monitor height
DISPLAY_TIME = 10       # seconds per image
BUFFER_SIZE = 5         # number of images to preload
IMAGE_ROTATION = 0      # allowed values: 0, 90, 180, 270

SEARCH_TERM = "flower"



def fetch_image_urls(
        search_term: str,
        max_results: int = 20) -> list:
    """
    Get a list of high-resolution images from Unsplash for the search term.
    Returns a list of URLs pointing to full-size images.
    """
    # Unsplash Source provides a direct random image URL per request
    urls = []
    for _ in range(max_results):
        # e.g., 800x800, flower keyword
        urls.append(f"https://source.unsplash.com/{MONITOR_WIDTH}x{MONITOR_HEIGHT}/?{search_term}")
    return urls

# def fetch_image_urls(
#         search_term: str,
#         max_results: int = 20) -> list:
#     """
#     Scrape Google Images search results and return image URLs.
#     """
#     # Parse the query properly.
#     query = quote(search_term)

#     # Build the URL.
#     url = f"https://www.google.com/search?q={query}&tbm=isch"

#     # Create the response.
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")

#     # Collect image URL's
#     image_urls = []

#     for img in soup.find_all("img"):
#         src = img.get("data-src") or img.get("src")
#         if src and src.startswith("http"): # type: ignore
#             image_urls.append(src)

#         if len(image_urls) >= max_results:
#             break

#     return image_urls


def download_image(
        url: str) -> np.ndarray | None:
    """
    Download an image and convert it to OpenCV format.
    """
    try:
        response = requests.get(url, timeout=5)
        image_array = np.asarray(
            bytearray(response.content),
            dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        return image

    except:
        return None


def crop_to_monitor_aspect(
        image: np.ndarray,
        target_width: int,
        target_height: int) -> np.ndarray:
    """
    Crop the center of the image to match the monitor aspect ratio.
    """
    # Get the monitor aspect ratio.
    target_ratio = target_width / target_height

    # Get the image aspect ratio.
    h, w = image.shape[:2]
    image_ratio = w / h

    # If the image is too wide, crop sides.
    if image_ratio > target_ratio:
        new_width = int(h * target_ratio)
        start_x = (w - new_width) // 2
        cropped = image[:, start_x:start_x + new_width]

        return cropped

    # If the image is too tall, crop top/bottom.
    elif image_ratio < target_ratio:
        new_height = int(w / target_ratio)
        start_y = (h - new_height) // 2
        cropped = image[start_y:start_y + new_height, :]

        return cropped

    # If the image happens to be exactly the right size, return it.
    # image_ratio == target_ratio
    else:
        return image


# def rotate_image(
#         image: np.ndarray,
#         rotation: int) -> np.ndarray:
#     """
#     Rotate image by 0, 90, 180, or 270 degrees.
#     """

#     if rotation == 90:
#         return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

#     if rotation == 180:
#         return cv2.rotate(image, cv2.ROTATE_180)

#     if rotation == 270:
#         return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

#     return image


def prepare_image(
        url: str) -> np.ndarray | None:
    """
    Full pipeline for preparing an image for display.
    """
    image = download_image(url)

    if image is None:
        return None

    else:
        image = crop_to_monitor_aspect(
            image,
            MONITOR_WIDTH,
            MONITOR_HEIGHT)
        image = cv2.resize(
            image,
            (MONITOR_WIDTH, MONITOR_HEIGHT),
            interpolation=cv2.INTER_AREA)

        return image


def buffer_loader(
        image_urls: list,
        buffer: deque) -> None:
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


def display_images(buffer):
    """
    Display images from buffer for DISPLAY_TIME seconds each.
    """
    cv2.namedWindow(
        "Display",
        cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        "Display",
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN)

    while True:
        if len(buffer) > 0:
            image = buffer.popleft()

            cv2.imshow("Display", image)
            cv2.waitKey(1)

            start = time.time()

            # Keep image visible for DISPLAY_TIME seconds
            while time.time() - start < DISPLAY_TIME:
                cv2.waitKey(1)

        else:
            time.sleep(0.1)



if __name__ == "__main__":
    print("Fetching flower image URLs...")

    image_urls = fetch_image_urls(SEARCH_TERM)

    print("Found", len(image_urls), "images")

    image_buffer = deque()

    # Start background loader thread.
    loader_thread = threading.Thread(
        target=buffer_loader,
        args=(image_urls, image_buffer),
        daemon=True
    )
    loader_thread.start()

    # Display images.
    display_images(image_buffer)
