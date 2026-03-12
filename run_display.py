import cv2
import numpy as np
import os
import random
import time
from typing import List



IMAGES_FOLDER: str = "display_images"
BATCH_SIZE: int = 1000
FPS: int = 60


def load_images(
        folder: str) -> List[np.ndarray]:
    """
    Load all images from a folder, ensuring they are the same size.

    Parameters
    ----------
    folder: str
        Path to the folder containing images.

    Returns
    -------
    List[np.ndarray]
        Loaded images as NumPy arrays.

    Raises
    ------
    ValueError
        If fewer than 2 images are found, images fail to load,
        or images have inconsistent dimensions.
    """
    # Find all supported image files
    image_files: List[str] = [f for f in os.listdir(folder)
                              if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    # Load images into a list of np.ndarray
    images: List[np.ndarray] = \
        [cv2.imread(os.path.join(folder, f)) for f in image_files]

    if len(images) < 2:
        raise ValueError("Need at least 2 images in the folder.")
    
    if any(img is None for img in images):
        raise ValueError("One or more images could not be loaded.")

    # Ensure all images are the same size
    first_shape = images[0].shape
    for img in images:
        if img.shape != first_shape:
            raise ValueError("All images must be the same size.")

    return images


def pick_next_image(
        current_index: int,
        images_count: int) -> int:
    """
    Pick the next image index, ensuring it is different
    from the current one.

    Parameters
    ----------
    current_index: int
        Index of the current image.
    images_count: int
        Total number of images available.

    Returns
    -------
    int
        Index of the next image.
    """
    choices: List[int] = list(range(images_count))
    choices.remove(current_index)
    return random.choice(choices)


def pixel_fade_transition(
        images: List[np.ndarray],
        batch_size: int = BATCH_SIZE,
        fps: int = FPS
    ) -> None:
    """
    Animate a pixel-by-pixel fade transition between images.

    Parameters
    ----------
    images: List[np.ndarray]
        List of images to display.
    batch_size: int, optional
        Number of pixels to swap per frame.
    fps: int, optional
        Frames per second for display.
    """
    # Get dimensions from first image
    h, w, c = images[0].shape

    # Setup OpenCV window
    cv2.namedWindow(
        "Pixel Fade Transition",
        cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        "Pixel Fade Transition",
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN)

    current_index: int = 0
    next_index: int = pick_next_image(current_index, len(images))
    current_img: np.ndarray = images[current_index].copy()
    target_img: np.ndarray = images[next_index]

    # Flatten images for easy pixel swapping
    current_flat: np.ndarray = current_img.reshape(-1, 3)
    target_flat: np.ndarray = target_img.reshape(-1, 3)

    # Track which pixels have not yet been flipped
    unflipped_pixels: np.ndarray = np.arange(h * w)

    while True:
        if len(unflipped_pixels) == 0:
            # Transition complete, pick next image
            current_index = next_index
            next_index = pick_next_image(current_index, len(images))
            current_img = images[current_index].copy()
            target_img = images[next_index]
            current_flat = current_img.reshape(-1, 3)
            target_flat = target_img.reshape(-1, 3)
            unflipped_pixels = np.arange(h * w)
            continue

        # Select a random batch of unflipped pixels
        current_batch_size: int = min(batch_size, len(unflipped_pixels))
        idx: np.ndarray = np.random.choice(
            unflipped_pixels,
            size=current_batch_size,
            replace=False)

        # Swap pixels
        current_flat[idx] = target_flat[idx]

        # Remove flipped pixels from the unflipped set
        unflipped_pixels = np.setdiff1d(
            unflipped_pixels,
            idx,
            assume_unique=True)

        # Display updated image
        cv2.imshow("Pixel Fade Transition", current_flat.reshape(h, w, 3))

        # Exit if ESC key is pressed
        if cv2.waitKey(1) == 27:
            break

        # Control frame rate
        time.sleep(1 / fps)

    cv2.destroyAllWindows()



if __name__ == "__main__":
    # Hide the mouse.
    os.system("unclutter -idle 0 &")

    # # Stream to the monitor.
    # os.system("export DISPLAY=:0")
    # time.sleep(1)

    # Rotate the monitor.
    os.system("WAYLAND_DISPLAY=wayland-0 wlr-randr --output HDMI-A-1 --transform 270")
    time.sleep(1)

    # # Create dummy windows to get full screen.
    # cv2.namedWindow("Display Image", cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty("Display Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Collect the images.
    images = load_images(IMAGES_FOLDER)

    # Begin displaying.
    pixel_fade_transition(images)
