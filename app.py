import streamlit as st
import numpy as np
import cv2
import hashlib
import io
import zipfile

from PIL import Image, ImageFilter, ImageEnhance
from streamlit_drawable_canvas import st_canvas


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="PixelCraft - Image Processing Studio",
    page_icon="🖼️",
    layout="wide"
)

st.title("🖼️ PixelCraft — Image Processing Studio")
st.write(
    "Upload your image once, select an operation, "
    "edit your image, and download the result."
)


# =====================================================
# 2. SESSION STATE
# =====================================================

defaults = {
    "original_image": None,
    "original_filename": "image.png",
    "upload_signature": None,
    "processed_image": None,
    "processed_label": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================================
# 3. HELPER FUNCTIONS
# =====================================================

def load_image(file):
    return Image.open(file).convert("RGB")


def pil_to_cv(image):
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def cv_to_pil(image):
    return Image.fromarray(
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    )


def save_result(image, label):
    st.session_state.processed_image = image
    st.session_state.processed_label = label


def show_comparison(original, edited, title="Processed Image"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(original, use_container_width=True)

    with col2:
        st.subheader(title)
        st.image(edited, use_container_width=True)


def download_image(image, filename="pixelcraft_result.png"):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    st.download_button(
        "⬇️ Download Image",
        data=buffer.getvalue(),
        file_name=filename,
        mime="image/png",
        key=f"download_{filename}"
    )


def make_grayscale(image):
    return image.convert("L").convert("RGB")


def make_binary(image, threshold):
    gray = np.array(image.convert("L"))
    result = np.where(gray >= threshold, 255, 0).astype(np.uint8)
    return Image.fromarray(result).convert("RGB")


def make_sketch(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    inverted = 255 - gray
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    inverted_blurred = 255 - blurred
    sketch = cv2.divide(gray, inverted_blurred, scale=256)
    return Image.fromarray(sketch).convert("RGB")


def pixelate_image(image, block_size):
    width, height = image.size

    small = image.resize(
        (
            max(1, width // block_size),
            max(1, height // block_size)
        ),
        Image.Resampling.NEAREST
    )

    return small.resize(
        (width, height),
        Image.Resampling.NEAREST
    )


def sharpen_image(image, amount):
    return ImageEnhance.Sharpness(image).enhance(amount)


def add_noise(image, noise_type, strength):
    array = np.array(image).astype(np.float32)

    if noise_type == "Gaussian":
        noise = np.random.normal(0, strength, array.shape)
        result = array + noise
    else:
        result = array.copy()
        probability = min(strength / 100, 0.5)

        random_map = np.random.random(
            (array.shape[0], array.shape[1])
        )

        result[random_map < probability / 2] = 0
        result[random_map > 1 - probability / 2] = 255

    return Image.fromarray(
        np.clip(result, 0, 255).astype(np.uint8)
    )


def change_background(image, color):
    image_bgr = pil_to_cv(image)
    height, width = image_bgr.shape[:2]

    if width < 3 or height < 3:
        raise ValueError("Image is too small.")

    mask = np.zeros((height, width), np.uint8)
    background_model = np.zeros((1, 65), np.float64)
    foreground_model = np.zeros((1, 65), np.float64)

    margin_x = max(1, int(width * 0.03))
    margin_y = max(1, int(height * 0.03))

    cv2.grabCut(
        image_bgr,
        mask,
        (
            margin_x,
            margin_y,
            max(1, width - 2 * margin_x),
            max(1, height - 2 * margin_y)
        ),
        background_model,
        foreground_model,
        5,
        cv2.GC_INIT_WITH_RECT
    )

    foreground_mask = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
        255,
        0
    ).astype(np.uint8)

    background = np.zeros_like(np.array(image))
    background[:] = color

    alpha = foreground_mask[:, :, None] / 255.0

    result = (
        np.array(image) * alpha
        + background * (1 - alpha)
    ).clip(0, 255).astype(np.uint8)

    return Image.fromarray(result)


def inpaint_image(image, mask):
    if mask is None or np.count_nonzero(mask) == 0:
        raise ValueError("Mark the area you want to remove.")

    image_bgr = pil_to_cv(image)

    mask = cv2.dilate(
        mask,
        np.ones((3, 3), np.uint8),
        iterations=1
    )

    result = cv2.inpaint(
        image_bgr,
        mask,
        5,
        cv2.INPAINT_TELEA
    )

    return cv_to_pil(result)


def resize_to_match(image, reference):
    return image.resize(
        reference.size,
        Image.Resampling.LANCZOS
    )


# =====================================================
# 4. SIDEBAR AND MAIN IMAGE UPLOAD
# =====================================================

st.sidebar.title("⚙️ Image Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload your main image",
    type=["png", "jpg", "jpeg", "bmp", "webp"],
    key="main_image_uploader"
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    signature = hashlib.md5(file_bytes).hexdigest()

    if signature != st.session_state.upload_signature:
        try:
            image = load_image(io.BytesIO(file_bytes))

            st.session_state.original_image = image
            st.session_state.original_filename = uploaded_file.name
            st.session_state.upload_signature = signature
            st.session_state.processed_image = None
            st.session_state.processed_label = ""

        except Exception as error:
            st.sidebar.error(f"Unable to load image: {error}")

if st.session_state.original_image is None:
    st.info("👈 Upload your image using the sidebar.")
    st.stop()

original = st.session_state.original_image

st.sidebar.success(
    f"Loaded: {st.session_state.original_filename}"
)

st.sidebar.caption(
    f"Size: {original.width} × {original.height} pixels"
)

operation = st.sidebar.radio(
    "Choose an operation",
    [
        "Original Image",
        "Grayscale / Black & White",
        "Pencil Sketch",
        "Pixelate Image",
        "Sharpen Image",
        "Resize Image",
        "Blend Two Images",
        "Change Background",
        "Remove Text / Objects",
        "Image Addition / Subtraction",
        "Add Noise",
        "Multiple Image Operations",
        "Multiple Image Gallery"
    ]
)


# =====================================================
# 5. ORIGINAL IMAGE
# =====================================================

if operation == "Original Image":
    st.header("Original Image")
    st.image(original, use_container_width=True)
    download_image(original, "pixelcraft_original.png")


# =====================================================
# 6. GRAYSCALE / BLACK & WHITE
# =====================================================

elif operation == "Grayscale / Black & White":
    st.header("Grayscale / Black & White")

    mode = st.radio(
        "Select mode",
        ["Grayscale", "Binary Black & White"],
        horizontal=True
    )

    if mode == "Grayscale":
        result = make_grayscale(original)
    else:
        threshold = st.slider("Threshold", 0, 255, 128)
        result = make_binary(original, threshold)

    save_result(result, mode)
    show_comparison(original, result, mode)
    download_image(result, "pixelcraft_grayscale.png")


# =====================================================
# 7. PENCIL SKETCH
# =====================================================

elif operation == "Pencil Sketch":
    st.header("Pencil Sketch")

    result = make_sketch(original)
    save_result(result, "Pencil Sketch")

    show_comparison(original, result, "Pencil Sketch")
    download_image(result, "pixelcraft_sketch.png")


# =====================================================
# 8. PIXELATE IMAGE
# =====================================================

elif operation == "Pixelate Image":
    st.header("Pixelate Image")

    block_size = st.select_slider(
        "Pixel block size",
        options=[8, 16, 32, 64],
        value=16
    )

    result = pixelate_image(original, block_size)
    save_result(result, "Pixelated Image")

    show_comparison(original, result, "Pixelated Image")
    download_image(result, "pixelcraft_pixelated.png")


# =====================================================
# 9. SHARPEN IMAGE
# =====================================================

elif operation == "Sharpen Image":
    st.header("Sharpen Image")

    amount = st.slider(
        "Sharpening strength",
        0.0, 5.0, 2.0, step=0.5
    )

    result = sharpen_image(original, amount)
    save_result(result, "Sharpened Image")

    show_comparison(original, result, "Sharpened Image")
    download_image(result, "pixelcraft_sharpened.png")


# =====================================================
# 10. RESIZE IMAGE
# =====================================================

elif operation == "Resize Image":
    st.header("Resize Image")

    col1, col2 = st.columns(2)

    with col1:
        new_width = st.number_input(
            "Width",
            min_value=1,
            max_value=10000,
            value=original.width
        )

    with col2:
        new_height = st.number_input(
            "Height",
            min_value=1,
            max_value=10000,
            value=original.height
        )

    result = original.resize(
        (int(new_width), int(new_height)),
        Image.Resampling.LANCZOS
    )

    save_result(result, "Resized Image")
    show_comparison(original, result, "Resized Image")
    download_image(result, "pixelcraft_resized.png")


# =====================================================
# 11. BLEND TWO IMAGES
# =====================================================

elif operation == "Blend Two Images":
    st.header("Blend Two Images")

    second_file = st.file_uploader(
        "Upload the second image",
        type=["png", "jpg", "jpeg", "bmp", "webp"],
        key="blend_uploader"
    )

    if second_file:
        second_image = resize_to_match(
            load_image(second_file),
            original
        )

        amount = st.slider(
            "Blend amount",
            0.0, 1.0, 0.5, step=0.05
        )

        result = Image.blend(original, second_image, amount)
        save_result(result, "Blended Image")

        show_comparison(original, result, "Blended Image")
        download_image(result, "pixelcraft_blended.png")
    else:
        st.info("Upload a second image to blend.")


# =====================================================
# 12. CHANGE BACKGROUND
# =====================================================

elif operation == "Change Background":
    st.header("Change Background")

    background_color = st.color_picker(
        "Choose background color",
        "#00AEEF"
    )

    if st.button("Change Background"):
        try:
            hex_color = background_color.lstrip("#")

            color = tuple(
                int(hex_color[i:i + 2], 16)
                for i in (0, 2, 4)
            )

            result = change_background(original, color)
            save_result(result, "Background Changed")

            show_comparison(original, result, "New Background")
            download_image(result, "pixelcraft_background.png")

        except Exception as error:
            st.error(f"Background change failed: {error}")



# =====================================================
# REMOVE TEXT / OBJECTS - FIXED VERSION
# =====================================================

elif operation == "Remove Text / Objects":
    st.header("🧹 Remove Text / Objects")

    st.write(
        "Paint over the text or object you want to remove, "
        "then click Remove Marked Text / Object."
    )

    st.warning(
        "Mark the entire text, including its edges. "
        "For best results, use a small brush and a simple background."
    )

    max_width = 700
    max_height = 600

    scale = min(
        max_width / original.width,
        max_height / original.height,
        1.0
    )

    canvas_width = max(1, int(original.width * scale))
    canvas_height = max(1, int(original.height * scale))

    canvas_background = original.resize(
        (canvas_width, canvas_height),
        Image.Resampling.LANCZOS
    )

    brush_size = st.slider(
        "Brush size",
        min_value=3,
        max_value=60,
        value=18,
        key="removal_brush_size"
    )

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 1.0)",
        stroke_width=brush_size,
        stroke_color="#FF0000",
        background_image=canvas_background,
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="freedraw",
        return_image_data=True,
        key="text_removal_canvas_fixed"
    )

    if st.button("Remove Marked Text / Object"):
        if canvas_result.image_data is None:
            st.error("Please draw over the text first.")

        else:
            # Read the canvas drawing.
            canvas_array = np.asarray(
                canvas_result.image_data
            )

            # Detect the red brush strokes.
            # The canvas background contains the original image,
            # so red pixels identify the marked region.
            red = canvas_array[:, :, 0].astype(np.int16)
            green = canvas_array[:, :, 1].astype(np.int16)
            blue = canvas_array[:, :, 2].astype(np.int16)

            small_mask = np.where(
                (red > 100) &
                (red > green * 1.25) &
                (red > blue * 1.25),
                255,
                0
            ).astype(np.uint8)

            # Enlarge the mask to cover text edges.
            kernel = np.ones((3, 3), np.uint8)
            small_mask = cv2.dilate(
                small_mask,
                kernel,
                iterations=2
            )

            # Resize the mask to match the original image.
            full_mask = cv2.resize(
                small_mask,
                (original.width, original.height),
                interpolation=cv2.INTER_NEAREST
            )

            marked_pixels = cv2.countNonZero(full_mask)

            if marked_pixels == 0:
                st.error(
                    "No marked area was detected. Paint over the "
                    "text again using the red brush."
                )

            else:
                # Display the mask for verification.
                with st.expander("Preview detected selection"):
                    st.image(
                        full_mask,
                        caption="White = area to remove",
                        clamp=True
                    )

                try:
                    original_bgr = cv2.cvtColor(
                        np.array(original),
                        cv2.COLOR_RGB2BGR
                    )

                    # OpenCV inpainting fills the marked area.
                    result_bgr = cv2.inpaint(
                        original_bgr,
                        full_mask,
                        5,
                        cv2.INPAINT_TELEA
                    )

                    result = Image.fromarray(
                        cv2.cvtColor(
                            result_bgr,
                            cv2.COLOR_BGR2RGB
                        )
                    )

                    save_result(
                        result,
                        "Text / Object Removed"
                    )

                    st.success(
                        "Removal complete. Check the edited image below."
                    )

                    show_comparison(
                        original,
                        result,
                        "Text / Object Removed"
                    )

                    download_image(
                        result,
                        "pixelcraft_text_removed.png"
                    )

                except Exception as error:
                    st.error(
                        f"Could not process the selection: {error}"
                    )


# =====================================================
# 14. IMAGE ADDITION / SUBTRACTION
# =====================================================

elif operation == "Image Addition / Subtraction":
    st.header("Image Addition / Subtraction")

    st.info(
        "Addition combines pixel intensities. Subtraction shows "
        "differences between images; it does not automatically remove text."
    )

    second_file = st.file_uploader(
        "Upload the second image",
        type=["png", "jpg", "jpeg", "bmp", "webp"],
        key="arithmetic_uploader"
    )

    action = st.radio(
        "Operation",
        ["Addition", "Subtraction"],
        horizontal=True
    )

    if second_file:
        second_image = resize_to_match(
            load_image(second_file),
            original
        )

        first_array = np.array(original).astype(np.int16)
        second_array = np.array(second_image).astype(np.int16)

        if action == "Addition":
            output = np.clip(
                first_array + second_array, 0, 255
            ).astype(np.uint8)
        else:
            output = np.abs(
                first_array - second_array
            ).astype(np.uint8)

        result = Image.fromarray(output)
        save_result(result, f"Image {action}")

        show_comparison(original, result, f"Image {action}")
        download_image(result, f"pixelcraft_{action.lower()}.png")
    else:
        st.info("Upload a second image to continue.")


# =====================================================
# 15. ADD NOISE
# =====================================================

elif operation == "Add Noise":
    st.header("Add Noise")

    noise_type = st.selectbox(
        "Noise type",
        ["Gaussian", "Salt & Pepper"]
    )

    strength = st.slider(
        "Noise strength",
        min_value=1,
        max_value=100,
        value=20
    )

    if st.button("Apply Noise"):
        result = add_noise(original, noise_type, strength)
        save_result(result, f"{noise_type} Noise")

        show_comparison(original, result, "Noisy Image")
        download_image(result, "pixelcraft_noise.png")


# =====================================================
# 16. MULTIPLE IMAGE OPERATIONS
# =====================================================

elif operation == "Multiple Image Operations":
    st.header("Multiple Image Operations")

    grayscale = st.checkbox("Grayscale")
    sketch = st.checkbox("Pencil Sketch")
    sharpen = st.checkbox("Sharpen")
    blur = st.checkbox("Gaussian Blur")
    invert = st.checkbox("Invert Colors")

    result = original.copy()

    if grayscale:
        result = make_grayscale(result)

    if sketch:
        result = make_sketch(result)

    if sharpen:
        result = sharpen_image(result, 2.0)

    if blur:
        result = result.filter(
            ImageFilter.GaussianBlur(radius=2)
        )

    if invert:
        result = Image.fromarray(
            (255 - np.array(result)).astype(np.uint8)
        )

    save_result(result, "Multiple Operations")

    show_comparison(original, result, "Processed Image")
    download_image(result, "pixelcraft_multiple_operations.png")


# =====================================================
# 17. MULTIPLE IMAGE GALLERY
# =====================================================

elif operation == "Multiple Image Gallery":
    st.header("Multiple Image Gallery")

    gallery_files = st.file_uploader(
        "Upload multiple images",
        type=["png", "jpg", "jpeg", "bmp", "webp"],
        accept_multiple_files=True,
        key="gallery_uploader"
    )

    if gallery_files:
        st.write(f"Uploaded {len(gallery_files)} image(s).")

        columns = st.columns(3)

        for index, file in enumerate(gallery_files):
            try:
                image = load_image(file)

                with columns[index % 3]:
                    st.image(
                        image,
                        caption=file.name,
                        use_container_width=True
                    )

            except Exception as error:
                st.warning(f"Could not load {file.name}: {error}")

        if st.button("Prepare ZIP Download"):
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(
                zip_buffer,
                "w",
                zipfile.ZIP_DEFLATED
            ) as archive:

                for file in gallery_files:
                    try:
                        image = load_image(file)
                        buffer = io.BytesIO()
                        image.save(buffer, format="PNG")

                        filename = file.name.rsplit(".", 1)[0] + ".png"
                        archive.writestr(filename, buffer.getvalue())

                    except Exception:
                        pass

            st.download_button(
                "⬇️ Download Gallery ZIP",
                data=zip_buffer.getvalue(),
                file_name="pixelcraft_gallery.zip",
                mime="application/zip",
                key="gallery_zip_download"
            )


# =====================================================
# 18. FOOTER
# =====================================================

st.sidebar.divider()
st.sidebar.caption("PixelCraft — Image Processing Studio")
st.sidebar.caption(
    "Built with Python, Streamlit, Pillow, NumPy and OpenCV."
)
