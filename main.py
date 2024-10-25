import dearpygui.dearpygui as dpg
from cryptography.fernet import *
import cryptography
import os
import time, sys
import DearPyGui_Animate.dearpygui_animate as animate
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

global_encrypt_add_input_id = 0
global_window_height=100
global_encrypt_possible_ids = []
global_decrypt_add_input_id = 0
global_decrypt_possible_ids = []
modified_files = []
show_load=False
cwd = os.getcwd()




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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def encrypt_file(item,f):
    with open(item, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)

    with open(item, 'wb') as file:
        file.write(encrypted_data)
        
    modified_files.append(item)
    
    print("Encrypting " + item)

def decrypt_file(item,f):
    try:
        with open(item, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)

        with open(item, 'wb') as file:
            file.write(decrypted_data)
            
        modified_files.append(item)
        print("Decrypting " + item)
        
    except (cryptography.fernet.InvalidToken, TypeError):
       modified_files.append("Error: Wrong Password or File Already Decrypted")
def run_folders(items,f, mode="enc"):
    
    for item in items:
        print(item)
        if(os.path.isfile(item)):
            if(mode == "enc"):
                encrypt_file(item,f)
            elif(mode=="dec"):
                decrypt_file(item,f)


        elif(os.path.isdir(item)):
            dir_items = []
            for path in os.listdir(item):
                dir_items.append(os.path.join(item, path))
            if(len(dir_items) !=0):
                print("accessing folder: " + item)
                run_folders(dir_items,f,mode)
            else:
                print ("Empty Folder")
        else:
            print("This file or folder doesn't exist")

def show_summary():
    global modified_files
    dpg.delete_item("child_summary", children_only=True)
    for i in modified_files:
        dpg.add_input_text(default_value=i, parent="child_summary", width=600)
    dpg.configure_item("summary", show=True)
    modified_files=[]
    


def encrypt_func():
    global show_load
    show_load = True

    key = generate_key(bytes(dpg.get_value(encrypt_key_input),"utf-8"))
    f = Fernet(key)
    items=[]

    for i in global_encrypt_possible_ids:
        
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
    
    run_folders(items,f, mode="dec")

    time.sleep(0.5)
    show_load = False
    show_summary()
    


def add_decrypt_input_table(placeholder = ""):
    global global_decrypt_add_input_id
    global global_decrypt_possible_ids
    with dpg.table(header_row=False, parent=decrypt_window, policy=dpg.mvTable_SizingFixedFit,tag=f"decrypt_input_table_{global_decrypt_add_input_id}"):
        dpg.add_table_column(init_width_or_weight=85)
        dpg.add_table_column()

        with dpg.table_row(tag=f"decrypt_input_row_{global_decrypt_add_input_id}"):
            dpg.add_button(indent=15,label="Remove", callback=remove_decrypt_input,tag=f"decrypt_remove_button_{global_decrypt_add_input_id}")
            if(placeholder==""):
                dpg.add_input_text( hint="Path to the Folder/File you want to decrypt", width=550, indent= 7,tag=f"decrypt_input_{global_decrypt_add_input_id}")
            else:
                dpg.add_input_text( default_value=placeholder, width=550, indent= 7,tag=f"decrypt_input_{global_decrypt_add_input_id}")
            global_decrypt_possible_ids.append(f"decrypt_input_{global_decrypt_add_input_id}")
            
    global_decrypt_add_input_id +=1    

def add_decrypt_new_input_button():
    with dpg.table(header_row=False, policy=dpg.mvTable_SizingFixedFit, parent=decrypt_window, tag="add_decrypt_button_table"):
        dpg.add_table_column(init_width_or_weight=495)
        dpg.add_table_column()
        with dpg.table_row():
            dpg.add_text()
            dpg.add_button(label="Add new File", indent=7, callback=add_decrypt_input, tag="add_decrypt_button")

def add_decrypt_input():
    global global_window_height
    if(global_window_height <160):
        global_window_height += 40
    dpg.configure_item(decrypt_window, height=global_window_height)
    dpg.delete_item("add_decrypt_button_table")
    add_decrypt_input_table()
    add_decrypt_new_input_button()
    
    


def add_encrypt_input_table(placeholder = ""):
    global global_encrypt_add_input_id
    global global_encrypt_possible_ids
    with dpg.table(header_row=False, parent=encrypt_window, policy=dpg.mvTable_SizingFixedFit,tag=f"encrypt_input_table_{global_encrypt_add_input_id}"):
        dpg.add_table_column(init_width_or_weight=550)
        dpg.add_table_column()

        with dpg.table_row(tag=f"encrypt_input_row_{global_encrypt_add_input_id}"):
            if(placeholder==""):
                dpg.add_input_text( hint="Path to the Folder/File you want to encrypt", width=550, indent= 7,tag=f"encrypt_input_{global_encrypt_add_input_id}")
            else:
                dpg.add_input_text( default_value=placeholder, width=550, indent= 7,tag=f"encrypt_input_{global_encrypt_add_input_id}")
            global_encrypt_possible_ids.append(f"encrypt_input_{global_encrypt_add_input_id}")
            dpg.add_button(label="Remove", callback=remove_encrypt_input,tag=f"encrypt_remove_button_{global_encrypt_add_input_id}")
    global_encrypt_add_input_id +=1

def add_encrypt_input():
    global global_window_height
    if(global_window_height <160):
        global_window_height += 40
    dpg.configure_item(encrypt_window, height=global_window_height)
    
    add_encrypt_input_table()
    dpg.delete_item("add_button")
    dpg.add_button(label="Add new File", indent=7, callback=add_encrypt_input, parent=encrypt_window, tag="add_button")
    

def remove_encrypt_input(sender, app_data, user_data):
    id = sender.split("_") 
    dpg.delete_item(f"encrypt_input_table_{id[-1]}")

def remove_decrypt_input(sender, app_data, user_data):
    id = sender.split("_") 
    dpg.delete_item(f"decrypt_input_table_{id[-1]}")


def encrypt_key_file_selected(sender, app_data, user_data):
    for x in app_data["selections"].values():
        dpg.configure_item(encrypt_key_input, default_value=x)

def decrypt_key_file_selected(sender, app_data, user_data):
    for x in app_data["selections"].values():
        dpg.configure_item(decrypt_key_input, default_value=x)

def decrypt_files_selected(sender, app_data, user_data):
    dpg.delete_item(decrypt_window,children_only=True)
    #dpg.configure_item(encrypt_path_input, show=False)
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


def encrypt_files_selected(sender, app_data, user_data):
    dpg.delete_item(encrypt_window,children_only=True)
    #dpg.configure_item(encrypt_path_input, show=False)
    if(sender != "encrypt_folder_dialog"):
        window_height=46 
        i=0
        for x in app_data["selections"].values():
            if(window_height <160):
                window_height += 40
            dpg.configure_item(encrypt_window, height=window_height)

            add_encrypt_input_table(placeholder=x)

        dpg.add_button(label="Add new File", indent=7, callback=add_encrypt_input, parent=encrypt_window, tag="add_button")
    else:
        add_encrypt_input_table(placeholder=app_data["file_path_name"])

def animation_func():
    animate.remove("encrypt_window_animation")
    animate.add("opacity", "encrypt_window", 0, 1, [.57, .06, .61, .86], 10, name="encrypt_window_animation")
    animate.remove("decrypt_window_animation")
    animate.add("opacity", "decrypt_window", 0, 1, [.57, .06, .61, .86], 10, name="decrypt_window_animation")



dpg.create_context()    


with dpg.font_registry():
    # first argument ids the path to the .ttf or .otf file
    title_font = dpg.add_font(resource_path("CONSOLA.TTF"), 50)
    main_font = dpg.add_font(resource_path("CONSOLA.TTF"), 20)


with dpg.file_dialog(directory_selector=False, show=False, callback=encrypt_files_selected,file_count=500, tag="encrypt_files_dialog", width=600 ,height=400, label="Select the files to encrypt"):
    dpg.add_file_extension(".*", color=(255, 255, 255))
    dpg.add_file_extension(".key", color=(255, 105, 97), custom_text="[!Key File]")

with dpg.file_dialog(directory_selector=False, show=False, callback=decrypt_files_selected,file_count=500, tag="decrypt_files_dialog", width=600 ,height=400, label="Select the files to decrypt"):
    dpg.add_file_extension(".*", color=(255, 255, 255))
    dpg.add_file_extension(".key", color=(255, 105, 97), custom_text="[!Key File]")

dpg.add_file_dialog(directory_selector=True, show=False, callback=encrypt_files_selected, tag="encrypt_folder_dialog", width=600 ,height=400, label="Select the folder to encrypt")
dpg.add_file_dialog(directory_selector=True, show=False, callback=decrypt_files_selected, tag="decrypt_folder_dialog", width=600 ,height=400, label="Select the folder to decrypt")

load_width_0, load_height_0, load_channels_0, load_data_0 = dpg.load_image(resource_path("img/0.png"))
load_width_1, load_height_1, load_channels_1, load_data_1 = dpg.load_image(resource_path("img/1.png"))
load_width_2, load_height_2, load_channels_2, load_data_2 = dpg.load_image(resource_path("img/2.png"))
load_width_3, load_height_3, load_channels_3, load_data_3 = dpg.load_image(resource_path("img/3.png"))
load_width_4, load_height_4, load_channels_4, load_data_4 = dpg.load_image(resource_path("img/4.png"))
load_width_5, load_height_5, load_channels_5, load_data_5 = dpg.load_image(resource_path("img/5.png"))
texture_data=[load_data_0,load_data_1,load_data_2,load_data_3,load_data_4,load_data_5]

with dpg.texture_registry():
    #dpg.add_static_texture(width=load_width, height=load_height, default_value=load_data, tag="load_texture")
    dpg.add_dynamic_texture(width=500, height=500, default_value=load_data_0, tag="loading_texture")




dpg.create_viewport(width=720, height=720, title="Lock Cypher: Encrypt / Decrypt your files", min_width=720, max_width=720,resizable=False,y_pos=10, small_icon=resource_path("logoT.ico"), large_icon=resource_path("logoT.ico"))
dpg.setup_dearpygui()


with dpg.window(label="Procesing", tag="loading",show=False):
    
    dpg.add_image("loading_texture")

with dpg.window(label="summary", tag="summary",show=False, min_size=(650,500), max_size=(650,500) ):
    dpg.add_text("Encrypted / Decrypted files")
    with dpg.child_window(tag="child_summary", height=390):
        pass
    dpg.add_button(label = "close", callback=lambda: dpg.configure_item("summary", show=False))

with dpg.window(tag="primary"):
    dpg.add_text("")
    with dpg.table(header_row=False,policy=dpg.mvTable_SizingFixedFit):
        
        dpg.add_table_column(init_width_or_weight=480)
        
        dpg.add_table_column()

        with dpg.table_row():
            
            encrypt_title = dpg.add_text("Encrypt", indent=15)
            dpg.bind_item_font(encrypt_title, title_font)

            decrypt_title =  dpg.add_text("Decrypt")
            dpg.bind_item_font(decrypt_title, title_font)

    toggle = dpg.add_slider_int(max_value=1, width=720, format="",callback=animation_func)
    dpg.add_text("")
    with dpg.table(header_row=False, tag="encrypt_window") as encrypt:
        dpg.add_table_column(width=700)
        with dpg.table_row(): 

            dpg.add_text("Introduce Password", indent=15)
                     
        with dpg.table_row():
            encrypt_key_input = dpg.add_input_text(indent=15, width=680, hint="Password", password=True)
                
        
        with dpg.table_row(): 
            dpg.add_text("")
        with dpg.table_row(): 
            dpg.add_text("Select the Folder/Files you want to encrypt",indent=15)
        
        with dpg.table_row():
            with dpg.child_window(height=100) as encrypt_window: 
                #encrypt_path_input = dpg.add_input_text(indent=15, width=950, hint="The path to the Folder/Files you want to encrypt")
                add_encrypt_input_table()
                dpg.add_button(label="Add new File", indent=7, callback=add_encrypt_input, parent=encrypt_window, tag="add_button")


        with dpg.table_row(): 
            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()

                with dpg.table_row():
                    dpg.add_button(label= "Browse Files to encrypt",indent=15, callback=lambda: dpg.show_item("encrypt_files_dialog"))
                    dpg.add_button(label= "Browse Folder to encrypt",indent=15, callback=lambda: dpg.show_item("encrypt_folder_dialog"))
        
        with dpg.table_row():
            dpg.add_text("")
        with dpg.table_row():
            dpg.add_button(label= "Encrypt Now",indent=15, callback=encrypt_func)
            
        
    
    with dpg.table(header_row=False,show=False,tag="decrypt_window") as decrypt:
        dpg.add_table_column()
        with dpg.table_row():
            with dpg.table(header_row=False, policy=dpg.mvTable_SizingFixedFit):
                dpg.add_table_column(init_width_or_weight=85)
                dpg.add_table_column()

                with dpg.table_row():
                    dpg.add_text("")  
                    dpg.add_text("Introduce the password you used to encrypt your Files")
        
        
        with dpg.table_row():
            decrypt_key_input = dpg.add_input_text(password=True,indent=15, width=660, hint="                                              Your password")
          
        
        with dpg.table_row():
            dpg.add_text("")
        
        with dpg.table_row():
            with dpg.table(header_row=False, policy=dpg.mvTable_SizingFixedFit):
                dpg.add_table_column(init_width_or_weight=194)
                dpg.add_table_column()

                with dpg.table_row():
                    dpg.add_text("")  
                    dpg.add_text("Select the Folder/Files you want to decrypt")
        with dpg.table_row():
            with dpg.child_window(height=100) as decrypt_window: 
                #encrypt_path_input = dpg.add_input_text(indent=15, width=950, hint="The path to the Folder/Files you want to encrypt")
                add_decrypt_input_table()
                add_decrypt_new_input_button()

        with dpg.table_row(): 
            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()

                with dpg.table_row():
                    dpg.add_button(label= "Browse Files to decrypt",indent=15, callback=lambda: dpg.show_item("decrypt_files_dialog"))
                    dpg.add_button(label= "Browse Folder to decrypt",indent=15, callback=lambda: dpg.show_item("decrypt_folder_dialog"))
        
        with dpg.table_row():
            dpg.add_text("")

        with dpg.table_row():
            with dpg.table(header_row=False, policy=dpg.mvTable_SizingFixedFit):
                dpg.add_table_column(init_width_or_weight=500)
                dpg.add_table_column()

                with dpg.table_row():
                    dpg.add_text("")  
                    dpg.add_button(label="Decrypt Now", callback=decrypt_func)

        

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


animation_func()
dpg.bind_theme(global_theme)

dpg.show_viewport() 
dpg.set_primary_window("primary", True)
#dpg.start_dearpygui()
gifcount = 0
gif_frame=0
window_indent=200
while dpg.is_dearpygui_running():
    animate.run()
    # insert here any code you would like to run in the render loop
    # you can manually stop by using stop_dearpygui()
    if(dpg.get_value(toggle)):
        dpg.configure_item(decrypt, show=True)
        dpg.configure_item(encrypt, show=False)

    else:
        dpg.configure_item(decrypt, show=False)
        dpg.configure_item(encrypt, show=True)
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