import numpy as np
import cv2
import pytesseract
from PIL import ImageGrab
import keyboard
import time
import tkinter as tk
import threading
import os
import ast
from tkinter import messagebox
from tkinter import filedialog
from functools import wraps
import traceback
import sys

def catch_all_errors():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # get the line number of the exception
                exc_type, exc_obj, tb = sys.exc_info()
                line_num = traceback.extract_tb(tb)[-1][1]
                # display error message in messagebox
                messagebox.showerror("Error", f"An error has occurred\nLine: {line_num}\nError: {str(e)}")
                print(f"An error has occurred\nLine: {line_num}\nError: {str(e)}")
        return wrapper
    return decorator

def catch_config_errors():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # get the line number of the exception
                exc_type, exc_obj, tb = sys.exc_info()
                line_num = traceback.extract_tb(tb)[-1][1]
                # display error message in messagebox
                messagebox.showerror("Error", f"An error has occurred\nLine: {line_num}\nError: {str(e)}\n\nPossibly the config file is corrupted\nTry deleting config.ini (located on this program directory) and restart the program.")
                print(f"An error has occurred\nLine: {line_num}\nError: {str(e)}")
        return wrapper
    return decorator


@catch_all_errors()
def longer_keypress(key):
    keyboard.press(key)
    time.sleep(0.2)
    keyboard.release(key)
    time.sleep(0.4)



# Define the path to the trained Tesseract data file
pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR/tesseract.exe'

# Create a label for the status
window = tk.Tk()


@catch_all_errors()
def on_closing():
    print('TK Window destroyed, executing SystemExit')
    window.destroy()  # hide the window instead of destroying it
    os._exit(1)

window.protocol("WM_DELETE_WINDOW", on_closing)  # bind the WM_DELETE_WINDOW event to on_closing

print('Yo sup, welcome to the debug cmd')

@catch_all_errors()
def update_timer():
    """Updates the timer label every 100 milliseconds"""
    global start_time
    elapsed_time = int(time.time() - start_time)
    hours = elapsed_time // 3600
    minutes = (elapsed_time % 3600) // 60
    seconds = elapsed_time % 60
    timer_label.config(text="Time elapsed: {:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))
    window.after(100, update_timer)

@catch_all_errors()
def start_ocr():
    global start_time
    status_label.config(text="OCR Running...")
    start_time = time.time()
    timer_label.grid(row=2, column=0, columnspan=3, padx=175, pady=10, sticky='w')
    status_label.grid(row=0, column=0, columnspan=3, padx=175, pady=10, sticky='w')
    update_timer()
    while(True):
      longer_keypress('right')
      longer_keypress('shift')
      time.sleep(0.2)
      with open('config.ini', 'r') as file:
          for line in file:
              if 'lighting' in line:
                  light_bool = line.split('=')[1].strip()
                  print(light_bool)
                  break

      with open('config.ini', 'r') as file:
          for line in file:
              if 'coords' in line:
                  # Split the line into a list of strings
                  global coords_str
                  coords_str = line.split('=')[1].strip()

      coords = ast.literal_eval(coords_str)

      if light_bool == 'False':
          coords.reverse()

      print(str(coords))
      
      # Initialize an empty list to store the OCR text for each coordinate
      ocr_texts = []
      
      # Grab a screenshot of the screen
      img = np.array(ImageGrab.grab())
      
      ## Convert the image to grayscale
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      
      #cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

      if light_bool == 'True':
       longer_keypress('left')
       zip_iterator = zip(reversed(range(len(coords))), coords)
          
      else:
       zip_iterator = zip(range(len(coords)), coords)

      for i, coord in zip_iterator:
           # Extract the ROI from the grayscale image
           x, y, w, h = coord
           roi = gray[y:y+h, x:x+w]
           
           # Define the gamma value
           gamma = 3.2      #2.5 sweet spot as it works, but 9 detected as 8, nobigdeal but yeah 3.5 does it but it detect 7 as 1  
           
           # Apply gamma correction to the ROI image
           roi_gamma = ((roi / 255.0) ** gamma) * 255.0
           
           # Convert the gamma-corrected ROI back to uint8
           roi_gamma = roi_gamma.astype(np.uint8)
           
           with open('config.ini', 'r') as file:
               for line in file:
                   if 'lang' in line:
                       langst = line.split('=')[1].strip()
                       break

           with open('config.ini', 'r') as file:
               for line in file:
                   if 'path' in line:
                       pathst = line.split('=')[1].strip()
                       break
           
           _, thresh = cv2.threshold(roi_gamma,0,255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
           
           if langst == 'custom':              
              # Set the configuration for Tesseract OCR

              traineddata_path = (str(pathst))

              # Extract the traineddata file name from the path
              traineddata_name = traineddata_path.split("/")[-1]
              
              # Set the configuration for pytesseract
              tessdata_dir_config = f'--tessdata-dir "{os.path.dirname(traineddata_path)}" -l {traineddata_name.split(".")[0]}'
              
              # Load the image and extract text using pytesseract

              # Load the language data file using Pytesseract
              text = pytesseract.image_to_string(thresh, config=tessdata_dir_config)
              #H0I
           else:
              text = pytesseract.image_to_string(thresh, lang=langst) 
           
           filtered_text = ''.join([c if c.isdigit() else '' for c in text])
         
           if 'E' in text and ('V' in text or 'N' in text or 'S' in text):
               text = '0'
               filtered_text = '0'      
               
               print('Executedd')
           list_of_exceptions = ['0', '']
         
           if text not in list_of_exceptions:
               char_to_num = {'K': '3', 'B': '8', 'I': '1', 'H': '2', 'U': '6', 'W': '2', 'E': '3'}
               output_list = []
               nums = []
               for c in text:
                   if c.isdigit():
                       nums.append(c)  # Keep digits as is
                   elif c in char_to_num:
                       nums.append(char_to_num[c])
                   elif c.isalpha():
                       continue  # Skip characters not in the dictionary
                   else:
                       nums.append(c)
               # Concatenate the numbers to create a new string
               new_s = ''.join(nums)
               # Append the new string to the output list
               output_list.append(new_s)
               filtered_text = ''.join(new_s)
               print(f'text before checking int 12: {text}')
               try:
                if int(filtered_text)<12:
                   print('Detected Under 12')
                   filtered_text = ''
               except:
                  print('EXCEPTION WARNING!')
                  pass

              
               #if filtered_text == '':
               #    filtered_text = '9223372036854775808'



           # Check if the filtered text is not empty before appending it to the list
           if light_bool == 'True':
            time.sleep(0.3)
           ocr_texts.insert(0, filtered_text) #append for normal 
           print(f'Coord {i+1} Unflitered: {text} Filtered: {filtered_text}')
           if light_bool == 'True':
            longer_keypress('up')
        
      if ocr_texts:
          # Find the index of the coordinate with the lowest OCR text
          ocr_ints = []
          for text in ocr_texts:
              if text.strip() != 'E':
                  try:
                      ocr_ints.append(int(text))
                  except ValueError:
                      if 'E' in text:
                          ocr_ints.append(1)
              else:
                  ocr_ints.append(999)
          min_value = min(ocr_ints)
          min_index = None
          for i, text in enumerate(ocr_texts):
              if text.strip() != 'E':
                  try:
                      if int(text) == min_value:
                          min_index = i
                          break
                  except ValueError:
                      pass
      
          print(f'Lowest = Slot {min_index+1}: {ocr_texts[min_index]}')
          print('LowIndex: ' + (str(min_index)))
          with open('config.ini', 'r') as file:
              for line in file:
                  if 'lighting' in line:
                      light_bool = line.split('=')[1].strip()
                      print(light_bool)
                      break

          if light_bool == 'True':
           print(f'Executing Bright OCR KeyPressDWN: Range (1, {min_index+1})')
           for i in range (1, (int(min_index+1))):
               longer_keypress('down')
               time.sleep(0.4)

          if light_bool == 'False':
           print(f'Executing Standard OCR KeyPressUP: Range (1, {min_index+1})')
           longer_keypress('left')
           for i in range (1, (int(min_index+1))):
               longer_keypress('up')
               time.sleep(0.4)
          

          longer_keypress('shift')
          longer_keypress('right')
          longer_keypress('f')
          longer_keypress('right')
          longer_keypress('down')
          longer_keypress('shift')
      else:
          # Print a message indicating that OCR was not able to detect any text in any of the ROIs
          print('OCR text not detected in any of the ROIs')
      time.sleep(34)
      longer_keypress('escape')
      longer_keypress('shift')
      time.sleep(2)

    
@catch_all_errors()
def firststart():
   with open('config.ini', 'w') as f:
     f.write('None' + '\n' + 'lang = mrz')

@catch_config_errors()
def roi_capturer():
  window.withdraw()
  bboxes = []
  cv2.waitKey(500)
  for i in range(1,7):
   # Grab a screenshot of the screen
   img = np.array(ImageGrab.grab())
   
   # Define the splash text
   splash_text = 'Slot: ' + (str(i)) + " Select a region of interest Press 'Enter' to confirm or 'C' to cancel"
   
   # Get the dimensions of the screen
   screen_height, screen_width, _ = img.shape
   
   # Set the font parameters
   font = cv2.FONT_HERSHEY_SIMPLEX
   font_scale = 1
   thickness = 2
   
   # Calculate the size of the text
   text_size, _ = cv2.getTextSize(splash_text, font, font_scale, thickness)
   
   # Calculate the coordinates of the text to center it on the screen
   text_x = int((screen_width - text_size[0]) / 2)
   text_y = int((screen_height + text_size[1]) / 2 * 0.10)
   
   # Add the text to the image
   cv2.putText(img, splash_text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
   
   # Create the ROI window and set it to a normal size
   cv2.namedWindow("Select ROI", cv2.WINDOW_NORMAL)
   
   # Set the ROI window to a maximized state
   cv2.setWindowProperty("Select ROI", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
   
   # Display the screenshot as the background of the ROI window
   cv2.imshow("Select ROI", img)
   
   # Freeze the screen for 2 seconds to allow for the new window animation effect to complete
   cv2.waitKey(350)
   
   # Get the selected ROI from the user
   #print("Select a region of interest on the screen...")
   bbox = cv2.selectROI("Select ROI", np.array(ImageGrab.grab()))
   if bbox == (0, 0, 0, 0):
       bboxes = []
       cv2.destroyWindow("Select ROI")
       break
       
  
   bboxes.insert(0, bbox)
   print(bbox)
   
   exec(f"bbox{i} = {bbox}")
   
   # Close the ROI window
   cv2.destroyWindow("Select ROI")
  
  try:
   window.deiconify()
   bbox1, bbox2, bbox3, bbox4, bbox5, bbox6 = bboxes
   print(bbox1)
   with open('config.ini', 'r') as f:
       lines = f.readlines()
   
   # Modify the first line of the list
   lines[0] = 'coords = ' + '[' + str(bbox1) + ',' + str(bbox2) + ',' + str(bbox3) + ',' + str(bbox4) + ',' + str(bbox5) + ',' + str(bbox6) + ']\n'
   
   with open('config.ini', 'w') as f:
       f.writelines(lines)
  
  
   with open('config.ini', 'r') as file:
       for line in file:
           if 'coords' in line:
               coords = line.split('=')[1].strip()
               print(coords)
               break
  except:
      pass

    
@catch_all_errors()
def run_ocr_thread():
    # Disable the "Start OCR" button
    start_ocr_button.config(state="disabled")
    settings_button.config(state="disabled")
    roi_capture_button.config(state="disabled")
    # Run the OCR function
    start_ocr()
   


@catch_all_errors()
def start_ocr_callback():
    # Disable the "Start OCR" button
    with open('config.ini', 'r') as file:
        for line in file:
            if 'None' in line:
                result = messagebox.askyesno('ROI Calibration', 'No ROI/Coordinate data found in config.ini, Run "Capture Region of Interest" for better results or would you like to use default ROI data?')
                if result == True:
                 search_string = "None"
                 found = False
                 with open("config.ini", "r") as f:
                     for line in f:
                         if search_string in line:
                             with open('config.ini', 'r') as f:
                                 lines = f.readlines()
                             
                             # Modify the first line of the list
                             lines[0] = 'coords = [(168, 737, 171, 46),(168, 648, 171, 45),(168, 555, 171, 45),(168, 464, 171, 45),(168, 374, 171, 45),(168, 287, 171, 45)]\n'
                             
                             with open('config.ini', 'w') as f:
                                 f.writelines(lines)
                
                             break

                if not result:
                   # User pressed "Cancel"
                   print('user pressed cancel')
                   return None



    start_ocr_button.config(state="disabled")
    settings_button.config(state="disabled")
    roi_capture_button.config(state="disabled")
    countdown = ["3", "2", "1"]
    for num in countdown:
        status_label.config(text=f"Starting in {num}...")
        window.update()
        time.sleep(1)

    
    # Create a new thread to run the OCR function
    ocr_thread = threading.Thread(target=run_ocr_thread)
    
    # Start the thread
    ocr_thread.start()

@catch_config_errors()
def show_settings():
    # Disable the main window
    window.attributes('-disabled', True)
    window.attributes("-topmost", False)

    # Create the settings window
    global settings_window
    settings_window = tk.Toplevel()
    settings_window.title("Settings")
    settings_window.geometry("500x230")
    settings_window.resizable(False, False)
    settings_window.focus_set()
    settings_window.lift()
    def closecallback():
        settings_window.destroy()
        window.attributes('-disabled', False)
        window.attributes("-topmost", True)
    settings_window.protocol("WM_DELETE_WINDOW", closecallback)  # bind the WM_DELETE_WINDOW event to on_closing
    settings_window.geometry("+{0}+{1}".format(int(window.winfo_screenwidth()/2 - 400/2), int(window.winfo_screenheight()/2 - 300/2)))

    # Create the settings widgets
    settings_label = tk.Label(settings_window, text="Settings")
    settings_label.pack(pady=10)
    
    # Create the selection option
    selection_frame = tk.Frame(settings_window)
    selection_frame.pack(padx=10, pady=10)
    
    selection_label = tk.Label(selection_frame, text="OCR Trained Data:")
    selection_label.pack(side="left")
    
    def saveset(new_line_text, line):
     # Read the contents of the file
     with open('config.ini', 'r') as f:
         lines = f.readlines()
     # Check if the second line already contains the new text
     if lines[line].strip() == new_line_text:
         pass
     else:
         # Replace or append the new text
         if len(lines) > 1:
             lines[line] = new_line_text + '\n'
         else:
             lines.append(new_line_text + '\n')
     
         # Write the updated lines to the file
         with open('config.ini', 'w') as f:
             f.writelines(lines)

    if not os.path.isfile('config.ini'):
        messagebox.showwarning('File not found', 'No config file found. creating a config file with the default region of interest')
        with open('config.ini', 'w') as f:
          f.write('coords = [(174, 282, 101, 48), (171, 376, 117, 46), (172, 464, 128, 52),(162, 558, 237, 44), (167, 645, 165, 47), (170, 736, 181, 47)]' + '\n' + 'lang = mrz')

    with open('config.ini', 'r') as file:
        for line in file:
            if 'lang' in line:
                language_set = line.split('=')[1].strip()
                print(language_set)
                break
    
    # Create the browse button
    browse_frame = tk.Frame(settings_window)
    browse_frame.pack(padx=10, pady=10)
    
    language_var = tk.StringVar(value=language_set)
    mrz_radio = tk.Radiobutton(selection_frame, text="Machine Readable Zone", variable=language_var, value="mrz")
    mrz_radio.pack(side="left", padx=5)
    
    eng_radio = tk.Radiobutton(selection_frame, text="Standard English", variable=language_var, value="eng")
    eng_radio.pack(side="bottom", padx=5)
    
    custom_radio = tk.Radiobutton(browse_frame, text="Custom OCR Trained Data: ", variable=language_var, value="custom")
    custom_radio.pack(side="left")


    browse_label = tk.Label(browse_frame, text="")
    browse_label.pack(side="left")
    
    with open('config.ini', 'r') as file:
        for line in file:
            if 'path' in line:
                paths = line.split('=')[1].strip()
                break

    try:
     path_var = tk.StringVar(value= (str(paths)))
    except:
     path_var = tk.StringVar(value="")
    path_entry = tk.Entry(browse_frame, textvariable=path_var)
    path_entry.pack(side="left")

    with open('config.ini', 'r') as file:
        for line in file:
            if 'lighting' in line:
                lights = line.split('=')[1].strip()
                print(lights)
                break

    lighting_var = tk.BooleanVar()
    lighting_var.set(lights)
    lighting_checkbutton = tk.Checkbutton(settings_window, text="Use cursor selection to read text more accurately (slower)", variable=lighting_var)
    lighting_checkbutton.pack(padx=10, pady=10)

    def accurate_lighting_callback():
        print("Use accurate text lighting:", lighting_var.get())
    
    lighting_checkbutton.config(command=accurate_lighting_callback)


    def browse_callback():
        selected_path = filedialog.askopenfilename(title = 'Browse File', filetypes=[("Tesseract Trained Data Files", "*.traineddata"), ("All Files", "*.*")])
        path_var.set(selected_path)
    
    browse_button = tk.Button(browse_frame, text="Browse", command=browse_callback)
    browse_button.pack(side="left", padx=5)
    
    def settings_ok_callback():
        selected_language = language_var.get()
        selected_checkbox = lighting_var.get()
        varied_lightning = ('lighting = ' + (str(selected_checkbox)))
        varied_language = ('lang = ' + selected_language)
        selected_paths = ('path = ' + path_var.get())


        saveset(selected_paths, 3)
        saveset(varied_language, 1)
        saveset(varied_lightning, 2)

        print("Selected language:", varied_language)
        closecallback()

    def advanced_callback():
        pass

    settings_ok_button = tk.Button(settings_window, text="OK", command=settings_ok_callback)
    settings_ok_button.config(width=10)
    settings_ok_button.pack(side="left", padx=10, pady=10)

    #advanced_button = tk.Button(settings_window, text="Advanced", command=advanced_callback)
    #advanced_button.config(width=10)
    #advanced_button.pack(side="right", padx=10, pady=10)

    
    settings_cancel_button = tk.Button(settings_window, text="Cancel", command=closecallback)
    settings_cancel_button.config(width=10)
    settings_cancel_button.pack(side="left", padx=10, pady=10)




@catch_all_errors()
def settings_ok_callback():
    # Save the settings and close the settings window
    # ...
    
    # Enable the main window
    settings_window.destroy()
    window.attributes('-disabled', False)
    window.attributes("-topmost", True)



@catch_all_errors()
def settings_cancel_callback():
    # Discard the settings and close the settings window
    # ...
    
    # Enable the main window
    settings_window.destroy()
    window.attributes('-disabled', False)
    window.attributes("-topmost", True)
    
    # Close the settings window

window.title("GTA Online Passive Money Generator Ver 0.8")

# Create the status label
status_label = tk.Label(window, text="AFK OCR Inside Track Bot", font=("Arial", 18))

# Create the "Start OCR" button
start_ocr_button = tk.Button(window, text="Start", font=("Arial", 12), command=start_ocr_callback)
start_ocr_button.config(width=10)

# Create the "Settings" button
settings_button = tk.Button(window, text="Settings", font=("Arial", 12), command=show_settings)
settings_button.config(width=10)


def show_text_frame():
    window.attributes('-disabled', True)
    window.attributes("-topmost", False)
    # Create the settings window
    global settings_window
    help_window = tk.Toplevel()
    help_window.title("Settings")
    help_window.geometry("800x320")
    help_window.resizable(False, False)
    help_window.focus_set()
    help_window.lift()
    def closecallback():
        help_window.destroy()
        window.attributes('-disabled', False)
        window.attributes("-topmost", True)
    help_window.protocol("WM_DELETE_WINDOW", closecallback)  # bind the WM_DELETE_WINDOW event to on_closing
    help_window.geometry("+{0}+{1}".format(int(window.winfo_screenwidth()/2 - 400/2), int(window.winfo_screenheight()/2 - 300/2)))

    # create a text frame
    text_frame = tk.Frame(help_window)
    text_frame.grid()

    # add text to the frame
    text_box = tk.Text(text_frame, height=18)
    text_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # add some example text to the text box
    example_text = 'Inside Track Horse Bot **VERSION 0.8 ONLY FOR PS4&PS5 VIA REMOTEPLAY**\n*PLEASE INSTALL DS4Emulator or reWASD (no config files yet for reWASD) and use this config: https://drive.google.com/file/d/1jet4G0rHFP6nH2pbxn_lRiLC9-RWfaoS/view*\n\nVideo Instruction for DS4Emulator: https://www.youtube.com/watch?v=GJdaLIUkmec\n\nIf this is your time starting, click on the "Capture Region of Interest" first, the region that you want to capture would be the horse track would be the odds of the horse (such as EVENS, 2/1, 3/1, 4/1, 16/1, 26/1, etc\nOnce thats done you can go ahead and click Start\n\nSettings: Language data can be obtained/downloaded from https://github.com/tesseract-ocr/tessdata, or https://github.com/tesseract-ocr/tessdata_best (CTRL + C to copy)'
    text_box.insert("end", example_text)

    # add a scrollbar to the text box
    scrollbar = tk.Scrollbar(text_frame, command=text_box.yview)
    scrollbar.grid(row=0, column=1, sticky="nswe")
    text_box.config(yscrollcommand=scrollbar.set)

    # add an OK button to close the window
    ok_button = tk.Button(text_frame, text="OK", command=closecallback, width=15)
    ok_button.grid(row=0, column=2, sticky="n", padx=1, pady=15)

menu_bar = tk.Menu(window)

# create a "Help" menu
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Get Started", command=show_text_frame)

# add the menus to the menu bar
menu_bar.add_cascade(label="Guide", menu=help_menu)

# display the menu bar
window.config(menu=menu_bar)

# Create the "Region of Interest" button
roi_capture_button = tk.Button(window, text="Capture Region of Interest", font=("Arial", 12), command=roi_capturer)

# Create the timer label
timer_label = tk.Label(window, text="Time elapsed: - seconds", font=("Arial", 12))

# Add widgets to the grid
status_label.grid(row=0, column=0, columnspan=3, padx=140, pady=10, sticky='w')
start_ocr_button.grid(row=1, column=0, padx=30, pady=10)
settings_button.grid(row=1, column=1, padx=30, pady=10)
roi_capture_button.grid(row=1, column=2, padx=30, pady=10)

# Attributes
window.geometry("+{0}+{1}".format(int(window.winfo_screenwidth()/2 - 685/2), int(window.winfo_screenheight()/2 - 300/2)))
window.attributes("-topmost", True)

# Set the window dimensions and disable resizing
window.geometry("580x155")
window.resizable(False, False)

# Add some padding to the left side of the window
window.focus_set()
window.lift()

if not os.path.isfile("config.ini"):
  with open('config.ini', 'w') as f:
   f.write('None' + '\n' + 'lang = mrz' + '\n' + 'lighting = True' + '\n' + 'path = ')


# Run the window
window.mainloop()