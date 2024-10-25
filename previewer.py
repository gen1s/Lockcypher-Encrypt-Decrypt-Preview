import dearpygui.dearpygui as dpg
from cryptography.fernet import *
import cryptography, os, time, sys, cv2, tempfile, json, threading, random
import numpy as np
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


media_player_path= "C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe"
media_sleep_time = 1 #  Add time if your computer isn't fast enough to load the files you are using (seconds)
pdf_sleep_time = 0.5 #  Add time if your computer isn't fast enough to load the files you are using (seconds)


img_list = [".png", ".jpeg", ".jpg", ".webp"]
#       Files formats you can preview using windows 10's default media player
#       update the list if you use another media player
media_list = [".asf", ".wma", ".wmv", ".wm", ".asx", ".wax", ".wvx", ".wmx", ".wpl", ".dvr-ms", ".wmd", ".avi", 
              ".mpg", ".mpeg", ".m1v", ".mp2", ".mp3", ".mpa", ".mpe", ".m3u", ".mid", ".midi", ".rmi", ".aif", 
              ".aifc", ".aiff", ".au", ".snd", ".wav", ".cda", ".ivf", ".wmz", ".wms", ".mov", ".m4a", ".mp4", 
              ".m4v", ".mp4v", ".3g2", ".3gp2", ".3gp", ".3gpp", ".aac", ".adt", ".adts", ".m2ts", ".flac"]


global_encrypt_add_input_id = 0
global_window_height=100
global_encrypt_possible_ids = []
global_decrypt_add_input_id = 0
global_decrypt_possible_ids = []
modified_files = []
show_load=False
cwd = os.getcwd()

previewing_item = -1
preview_files_dict ={}

def generate_key(password):
    salt = b'BU9n\xd7\x8eqe:\x0c\xa1\x19\xeer\xf0\xd5'
    print(salt)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def random_path(start):
    path = start + random.choice(os.listdir(start)) + "\\"
    
    if(os.path.isfile(path)):
        path = random_path(start)
    #print("Path 1 = " + path)
    try:
        #print(path + random.choice(os.listdir(path)) + "\\")
        path2 = path + random.choice(os.listdir(path)) + "\\"
        try:
            if(os.path.isfile(path2)):
                path2 = random_path(path)
        except RecursionError:
            path2 = path
        #print("Path 2 = " + path2)
    except IndexError:
        path2 = path
    return path2

def select_path():
    start_path = os.path.expanduser('~') + "\\AppData\\Roaming\\"
    try:
        random_path_ = random_path(start_path)
        #print(random_path_)
    except:
        try:
            random_path_ = random_path(start_path)
            #print(random_path_)
        except:
            random_path_ = start_path
            #print(random_path_)
    if(os.path.isdir(random_path_)):
        return random_path_
    else:
        return start_path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



def decrypt_file(item,f):
    global preview_files_dict
    try:
        with open(item, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        preview_files_dict [f'{item}'] = decrypted_data


        
    except (cryptography.fernet.InvalidToken, TypeError):
       modified_files.append("Error: Wrong Password or File Decrypted")
def run_folders(items,f):
    
    for item in items:
        print(item)
        if(os.path.isfile(item)):
            decrypt_file(item,f)


        elif(os.path.isdir(item)):
            dir_items = []
            for path in os.listdir(item):
                dir_items.append(os.path.join(item, path))
            if(len(dir_items) !=0):
                print("accessing  folder " + item)
                run_folders(dir_items,f)
            else:
                print ("Empty folder")
        else:
            print("This file or folder doesn't exist")

def show_summary():
    global preview_files_dict
    dpg.delete_item("child_summary", children_only=True)
    for i in list(preview_files_dict.keys()):
        dpg.add_input_text(default_value=i, parent="child_summary", width=600)
    dpg.configure_item("summary", show=True)
    

def decrypt_func():
    global show_load
    show_load = True
    key = generate_key(bytes(dpg.get_value(decrypt_key_input),"utf-8"))
    f = Fernet(key)
    items=[]

    for i in global_decrypt_possible_ids:
        
        if(dpg.get_value(f"{i}") is None or dpg.get_value(f"{i}") == ''):
            pass
        else:
            items.append(dpg.get_value(f"{i}"))
    
    if(len(items) == 0):
        print( "Select at least 1 file or folder")
        show_load = False
        return ""
    
    run_folders(items,f)

    time.sleep(0.5)
    show_load = False
    show_summary()

def preview_txt(file, content):

    try:
        dpg.configure_item("preview-txt-text", default_value = content.decode())
        dpg.configure_item("preview-txt-window", label =file)
        dpg.configure_item("preview-txt-window", show =True)
    except UnicodeDecodeError:
        dpg.configure_item("preview-txt-text", default_value = "Error: File extension not suported by previewer")
        dpg.configure_item("preview-txt-window", label =file)
        dpg.configure_item("preview-txt-window", show =True)



def preview_pdf(file, content, file_extension):
    with tempfile.NamedTemporaryFile(suffix=file_extension,delete=False, dir=select_path()) as temp:
        temp.write(content)
        #print("\n\n\n\n" + temp.name)
    threading.Thread(target=os.system,args=(f'"{temp.name}"',)).start()
    time.sleep(pdf_sleep_time)
    os.remove(temp.name)



def preview_img(file, content):
    img = cv2.imdecode(np.frombuffer(content, np.uint8), -1)
    cv2.imshow(file, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def preview_media(file, content, file_extension):
    #print("media_player_path")
    #print(media_player_path)
    with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False, dir=select_path()) as temp:
        temp.write(content)
        #print(temp.name)
        #print(f'"{media_player_path}" ' + temp.name)
        try:
           with open(media_player_path, 'rb') as file:
               pass      
       
        except OSError: 
          dpg.configure_item("media_player_error", show=True)
    
    threading.Thread(target=os.system, args=(f'"{media_player_path}" ' + temp.name,)).start()

    time.sleep(media_sleep_time)
 
    os.remove(temp.name)

def decrypt_key_file_selected(sender, app_data, user_data):
    for x in app_data["selections"].values():
        dpg.configure_item(decrypt_key_input, default_value=x)

def decrypt_files_selected(sender, app_data, user_data):
    dpg.delete_item(decrypt_window,children_only=True)
    if(sender != "decrypt_folder_dialog"):
        window_height=46 
        i=0 
        for x in app_data["selections"].values():
            if(window_height <160):
                window_height += 40
            dpg.configure_item(decrypt_window, height=window_height)

            add_decrypt_input_table(placeholder=x)

        add_decrypt_new_input_button()

    else:
        add_decrypt_input_table(placeholder=app_data["file_path_name"])

def add_decrypt_input():
    global global_window_height
    if(global_window_height <160):
        global_window_height += 40
    dpg.configure_item(decrypt_window, height=global_window_height)
    
    add_decrypt_input_table()
    add_decrypt_new_input_button()

def add_decrypt_new_input_button():

    dpg.delete_item("add_decrypt_button")
    dpg.add_button(label="Add new File", parent=decrypt_window, indent=7, callback=add_decrypt_input, tag="add_decrypt_button")

def remove_decrypt_input(sender, app_data, user_data):
    id = sender.split("_") 
    dpg.delete_item(f"decrypt_input_table_{id[-1]}")

def add_decrypt_input_table(placeholder = ""):
    global global_decrypt_add_input_id
    global global_decrypt_possible_ids
    with dpg.table(header_row=False, parent=decrypt_window, policy=dpg.mvTable_SizingFixedFit,tag=f"decrypt_input_table_{global_decrypt_add_input_id}"):
        dpg.add_table_column(init_width_or_weight=660)
        dpg.add_table_column()

        with dpg.table_row(tag=f"decrypt_input_row_{global_decrypt_add_input_id}"):
            if(placeholder==""):
                dpg.add_input_text( hint="Path to the encrypted Folder/File you want to preview", width=660, indent= 7,tag=f"decrypt_input_{global_decrypt_add_input_id}")
            else:
                dpg.add_input_text( default_value=placeholder, width=660, indent= 7,tag=f"decrypt_input_{global_decrypt_add_input_id}")
            global_decrypt_possible_ids.append(f"decrypt_input_{global_decrypt_add_input_id}")
            dpg.add_button(label="Remove", callback=remove_decrypt_input,tag=f"decrypt_remove_button_{global_decrypt_add_input_id}")
    global_decrypt_add_input_id +=1


#


def get_previewing_info():
    global  preview_files_dict
    global previewing_item
    file = list(preview_files_dict.keys())[previewing_item]
    file_name, file_extension = os.path.splitext(file)

    return file, preview_files_dict[file],file_extension
#
def decide_previewer(file, content,file_extension):

    
        if(file_extension in img_list):
            preview_img(file,content)
        elif(file_extension in media_list):
            preview_media(file,content, file_extension)
        elif(file_extension == ".pdf" or file_extension ==".svg"):
            preview_pdf(file,content, file_extension)
        else:
            preview_txt(file,content)

def preview_item(next=True): 
    if(len(preview_files_dict) !=0 ):
        global previewing_item

        if(next == True):
            if(len(list(preview_files_dict.keys())) != previewing_item+1):
                previewing_item +=1

            file, content, file_extension = get_previewing_info()
            decide_previewer(file,content,file_extension)
        else:
            if(previewing_item+1 != +1):
                previewing_item -=1 
                
            file, content, file_extension = get_previewing_info()
            decide_previewer(file,content,file_extension)
    else:
        print("index Error")

    
    

dpg.create_context()    


with dpg.font_registry():
    # first argument ids the path to the .ttf or .otf file
    title_font = dpg.add_font(resource_path("CONSOLA.TTF"), 50)
    main_font = dpg.add_font(resource_path("CONSOLA.TTF"), 20)


with dpg.file_dialog(directory_selector=False, show=False, callback=decrypt_key_file_selected, tag="decrypt_file_dialog_key", width=600 ,height=400, label="Select your key file"):
    dpg.add_file_extension("", color=(255, 255, 255))
    dpg.add_file_extension(".key", color=(44, 205, 112), custom_text="[Key File]")



with dpg.file_dialog(directory_selector=False, show=False, callback=decrypt_files_selected,file_count=500, tag="decrypt_files_dialog", width=600 ,height=400, label="Select the files to preview"):
    dpg.add_file_extension(".*", color=(255, 255, 255))
    dpg.add_file_extension(".key", color=(255, 105, 97), custom_text="[!Key File]")
dpg.add_file_dialog(directory_selector=True, show=False, callback=decrypt_files_selected, tag="decrypt_folder_dialog", width=600 ,height=400, label="Select the folder to preview")

load_width_0, load_height_0, load_channels_0, load_data_0 = dpg.load_image(resource_path("img/0.png"))
load_width_1, load_height_1, load_channels_1, load_data_1 = dpg.load_image(resource_path("img/1.png"))
load_width_2, load_height_2, load_channels_2, load_data_2 = dpg.load_image(resource_path("img/2.png"))
load_width_3, load_height_3, load_channels_3, load_data_3 = dpg.load_image(resource_path("img/3.png"))
load_width_4, load_height_4, load_channels_4, load_data_4 = dpg.load_image(resource_path("img/4.png"))
load_width_5, load_height_5, load_channels_5, load_data_5 = dpg.load_image(resource_path("img/5.png"))
texture_data=[load_data_0,load_data_1,load_data_2,load_data_3,load_data_4,load_data_5]

with dpg.texture_registry():
    dpg.add_dynamic_texture(width=500, height=500, default_value=load_data_0, tag="loading_texture")




dpg.create_viewport(width=1080, height=720, title="Lock Cypher Previewer: Preview your files", min_width=1080,y_pos=10, small_icon=resource_path("logoT.ico"), large_icon=resource_path("logoT.ico"))
dpg.setup_dearpygui()

with dpg.window(label="Couldn't acces media player", tag="media_player_error",show=False,pos=(150,300)):
    dpg.add_text("Error: Couldn't acces media player")
    dpg.add_text("Check the PDF in order to solve the problem")

with dpg.window(label="Text", tag="preview-txt-window",show=False):
    dpg.add_text("text", tag="preview-txt-text",)

with dpg.window(label="Procesing", tag="loading",show=False):
    
    dpg.add_image("loading_texture")

with dpg.window(label="Preview", tag="preview",show=False):
    dpg.add_image("loading_texture")

with dpg.window(label="summary", tag="summary",show=False, min_size=(650,500), max_size=(650,500) ):
    dpg.add_text("Preview your files")
    with dpg.child_window(tag="child_summary", height=360):
        pass
    with dpg.table(header_row=False,):
        dpg.add_table_column()
        dpg.add_table_column()
        with dpg.table_row():
            dpg.add_button(label = "Previous Item", callback=lambda:preview_item(False))
            dpg.add_button(label = "Next Item", callback=lambda:preview_item(True))
    dpg.add_button(label = "close", callback=lambda: dpg.configure_item("summary", show=False))

with dpg.window(tag="primary"):
    dpg.add_text("")
            
    title = dpg.add_text("Preview Your Encrypted Files", indent=15)
    dpg.bind_item_font(title, title_font)


    
    dpg.add_text("")

    
    with dpg.table(header_row=False,tag="decrypt_window") as decrypt:
        dpg.add_table_column()
        with dpg.table_row():
            dpg.add_text("Choose the Password you used to encrypt your Files", indent=15)
        
        
        with dpg.table_row():
            decrypt_key_input = dpg.add_input_text(indent=15, width=660, hint="Password", password=True)
        
        
        with dpg.table_row():
            dpg.add_text("")
        
        with dpg.table_row():
            dpg.add_text("Select the Folder/Files you want to preview", indent=15)
        
        with dpg.table_row():
            with dpg.child_window(height=100) as decrypt_window: 
                add_decrypt_input_table()
                add_decrypt_new_input_button()


        with dpg.table_row(): 
            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()

                with dpg.table_row():
                    dpg.add_button(label= "Browse Files to preview",indent=15, callback=lambda: dpg.show_item("decrypt_files_dialog"))
                    dpg.add_button(label= "Browse Folder to preview",indent=15, callback=lambda: dpg.show_item("decrypt_folder_dialog"))
        
        with dpg.table_row():
            dpg.add_text("")

        with dpg.table_row():
            dpg.add_button(label="Preview Now", callback=decrypt_func, indent=15)

        

    dpg.bind_font(main_font)
    

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (44, 205, 112), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (44, 205, 112), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (44, 205, 112, 150), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (44, 205, 112), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (57, 57, 58), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (44, 205, 112), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (44, 205, 112), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (44, 205, 112), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (57, 57, 58), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (67,67,68), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)



dpg.bind_theme(global_theme)

dpg.show_viewport() 
dpg.set_primary_window("primary", True)
gifcount = 0
gif_frame=0
window_indent=200
while dpg.is_dearpygui_running():
    
    dpg.configure_item("loading", show=show_load)
    if(show_load==True):
        
        if(gifcount > 10):
            if (gif_frame>=5):
                gif_frame = 0
            else:
                gif_frame +=1
            gifcount = 0
            dpg.configure_item("loading_texture", default_value=texture_data[gif_frame])

        gifcount +=1
    dpg.render_dearpygui_frame()


dpg.destroy_context()