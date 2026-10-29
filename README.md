# 🎨 PixelCraft – Image Processing Studio

PixelCraft is a web-based image processing application developed using Python and Streamlit. It allows users to upload images, apply various image processing techniques, preview the results, and download processed images through a simple, interactive interface.

The project uses GitHub for source code management and Streamlit Community Cloud for deployment.

## 🌐 Live Demo

🚀 **Try the application online:**

[Open PixelCraft – Image Processing Studio](https://pragyanaipixelcraftimageprocessingstudio-gobjyscdr7ktsrczpgnpw.streamlit.app/)

Replace `YOUR-STREAMLIT-APP-URL` with your actual deployed Streamlit application URL.

## 🚀 Features

- 📤 **Image Upload:** Upload an image for processing.
- ⚫ **Grayscale Conversion:** Convert color images into grayscale.
- ◼️ **Binary Image Conversion:** Convert grayscale images into black-and-white images using thresholding.
- ✏️ **Pencil Sketch:** Transform images into pencil sketch effects.
- 🟪 **Pixelation:** Apply different pixelation levels, including 8, 16, 32, and 64.
- 🔍 **Image Sharpening:** Enhance image edges and details.
- 📐 **Image Resizing:** Resize images to the desired dimensions.
- 🖼️ **Image Blending:** Combine two images into a single image.
- 🎨 **Background Color Replacement:** Replace selected background areas with a different color.
- 🧹 **Text and Object Removal:** Mark unwanted areas and attempt to remove them using image inpainting.
- ➕ **Image Addition:** Perform pixel-wise image addition.
- ➖ **Image Subtraction:** Perform pixel-wise image subtraction.
- 🌫️ **Noise Addition:** Add noise effects to images.
- 🧰 **Multiple Image Operations:** Apply available processing techniques through the interface.
- 🖼️ **Processed Image Gallery:** View processed images.
- 📥 **Download Results:** Download processed images and ZIP archives where supported.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application interface |
| Pillow (PIL) | Image loading, conversion, and resizing |
| NumPy | Pixel calculations and array operations |
| OpenCV | Image filtering, processing, and inpainting |
| streamlit-drawable-canvas | Interactive image marking |
| GitHub | Source code hosting and project management |
| Streamlit Community Cloud | Application deployment |

## 📂 Project Structure

```text
PixelCraft-Image-Processing-Studio/
│
├── app.py
├── requirements.txt
└── README.md
```

## ⚙️ Requirements

The application uses the following Python libraries. Make sure your `requirements.txt` contains:

```text
streamlit
pillow
numpy
opencv-python-headless
streamlit-drawable-canvas
```

## 🚀 Deployment Using GitHub and Streamlit

This project can be managed directly through GitHub and deployed using Streamlit Community Cloud. VS Code is not required for this workflow.

### Step 1: Upload Project Files to GitHub

Create or open your GitHub repository and ensure that it contains:

- `app.py`
- `requirements.txt`
- `README.md`

### Step 2: Open Streamlit Community Cloud

Visit [Streamlit Community Cloud](https://share.streamlit.io/) and sign in using your GitHub account.

### Step 3: Deploy the Application

1. Click **Create app**.
2. Select your GitHub repository.
3. Choose the correct branch.
4. Set the main file path to `app.py`.
5. Click **Deploy**.

Streamlit will install the dependencies listed in `requirements.txt` and launch the application.

### Step 4: Update Your Application

When you edit and commit `app.py` or other project files through GitHub, Streamlit Community Cloud will normally detect the changes and redeploy the application.

## 🖥️ How to Use

1. Open the deployed PixelCraft web application.
2. Upload your main image.
3. Select the desired image processing operation.
4. Adjust the available settings, such as threshold, image dimensions, pixelation level, or brush size.
5. Preview the processed image.
6. Download the result to your device.
7. Repeat with other supported operations as required.

**Note:** The available operations depend on the current implementation. Text and object removal uses image inpainting, and results depend on the selected region and surrounding image content.

## 🎯 Project Objectives

- Understand fundamental image processing techniques.
- Learn how digital images are represented as pixels and arrays.
- Implement image transformations using Python libraries.
- Explore filtering, thresholding, blending, and inpainting.
- Develop an interactive image processing web application.
- Practice GitHub-based source code management.
- Learn application deployment using Streamlit Community Cloud.

## 📚 Key Learnings

- Image manipulation using Pillow and NumPy.
- Grayscale and binary image conversion.
- Image resizing and pixelation.
- Image sharpening and noise processing.
- Image blending and pixel-wise arithmetic.
- Image masks and inpainting using OpenCV.
- Interactive interface development using Streamlit.
- Dependency management and cloud deployment.

## 🔮 Future Enhancements

- Add more image filters and enhancement techniques.
- Improve text and object removal.
- Introduce automatic background removal.
- Add batch image processing.
- Improve image comparison and preview options.
- Support additional image formats and export options.

## 👨‍💻 Author

**Ajay saware**

**Project Title:** PixelCraft – Image Processing Studio

**Technologies:** Python, Streamlit, Pillow, NumPy, and OpenCV.

**Source Code:** Hosted on GitHub.

**Deployment:** Streamlit Community Cloud.


⭐ If you find this project useful, consider giving the repository a star on GitHub!
