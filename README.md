# Capture and GPT Assistant

This project provides a tool to capture a selected area of the screen, perform OCR (Optical Character Recognition) on the captured image, and then use the OpenAI GPT API to get intelligent responses based on the extracted text.

## Prerequisites

- Python 3.x
- `pip` (Python package installer)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-repo/capture-gpt-assistant.git
   cd capture-gpt-assistant
   ```

2. **Set up a virtual environment:**

   ```bash
   python3 -m venv myenv
   source myenv/bin/activate  # On Windows, use `myenv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```bash
   pip install pytesseract pillow openai screeninfo python-dotenv
   ```

4. **Install Tkinter:**

   - **Windows:**
     Tkinter is usually included with Python on Windows. No additional installation should be needed.

   - **macOS:**
     Tkinter is also included with Python on macOS, but if you encounter issues, you can install it via Homebrew:
     ```bash
     brew install python-tk
     ```

   - **Linux (Debian/Ubuntu):**
     Install Tkinter using apt-get:
     ```bash
     sudo apt-get install python3-tk
     ```

5. **Install Tesseract:**

   - **On Debian/Ubuntu:**

     ```bash
     sudo apt-get install tesseract-ocr
     ```

   - **On macOS:**

     ```bash
     brew install tesseract
     ```

   - **On Windows:**
     Download and install Tesseract from [this link](https://github.com/tesseract-ocr/tesseract).

6. **Set up the environment variables:**

    Create a `.env` file in the project directory and add the following environment variables:
    
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    TESSERACT_CMD_PATH=/
    ```
    
     Replace `your_openai_api_key` with your actual OpenAI API key.

7. **Set up the Tesseract path:**

   Make sure the Tesseract executable is in your system's PATH. If not, update the path in the script:

   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update if necessary
   ```

8. **Configure the OpenAI API key:**

   Obtain your API key from [OpenAI](https://platform.openai.com/account/api-keys) and set it in the script:

   ```python
   openai.api_key = 'YOUR_API_KEY'
   ```

## Usage

1. **Run the script:**

   ```bash
   python capture_gpt.py
   ```

2. **Using the tool:**

   - **Select Area:** Click on "Select Area" to define the area of the screen to capture. Click and drag to create a rectangle over the area you want to capture.
   - **Capture and Get Response:** After selecting the area, click on "Capture and Get Response" to capture the selected area, extract text using OCR, and get a response from GPT.

## Customizing the Pre-Prompt

The script includes a pre-prompt to help the GPT model understand the context of the captured text. You can customize this pre-prompt to better suit your needs.

1. **Locate the pre-prompt definition in the script:**

   ```python
   pre_prompt = "You are a smart assistant. Answer the following questions clearly and concisely:\n\n"
   ```

2. **Modify the pre-prompt to fit your specific context:**

   For example, if you're asking technical questions, you might change it to:

   ```python
   pre_prompt = "You are a technical expert. Provide detailed and accurate answers to the following questions:\n\n"
   ```

3. **Save the script after making your changes.**

By customizing the pre-prompt, you can guide the GPT model to provide more relevant and accurate responses based on the specific context of your captured text.

## Script Overview

### Main Functions:

- **capture_screen_area(x1, y1, x2, y2):** Captures the specified area of the screen and saves it as an image.
- **ocr_image(image_path):** Performs OCR on the captured image to extract text.
- **get_gpt_response(question):** Sends the extracted text to the OpenAI GPT API to get a response.
- **select_area():** Opens a transparent window to allow the user to select an area of the screen.
- **on_area_selected(x1, y1, x2, y2):** Callback function that stores the selected area.
- **capture_and_process():** Captures the stored area and processes the text using OCR and GPT.

### Classes:

- **AreaSelector:** Handles the selection of the screen area with a transparent overlay.

## License

This project is licensed under the MIT License.