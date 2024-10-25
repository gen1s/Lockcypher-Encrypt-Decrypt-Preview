# Lockcypher Encrypt Decrypt and Preview Your files

Main.py
---------------------------------------------------
The main.py file encrypts and decrypts files or folders. It uses the Fernet library to do so.
You can toggle between Encrypt and Decrypt mode by clicking on the bar under each word.

To Encrypt:
 - Insert a password (there are no requirements)
 - Browse the files or folder you want to encrypt
 - Click on "Encrypt Now"

To Decrypt:
 - Select Decrypt mode
 - Insert the password you used to encrypt
 - Browse the files or folder you want to decrypt
 - Click on "Decrypt Now"

Previewer.py
------------------------------------------------
With the previewer.py file, you can preview encrypted files without decrypting them, making them always secure.
(For pdf or media files a temporary file will be created on a random folder containing the decrypted data of the selected file for a short period before deleting it.
The default is 0.5 seconds for pdf files and 1 second for media files)

To preview encrypted files:
 - Insert the password you used to encrypt
 - Browse the files or folder you want to preview
 - Click on "Preview Now"
 - Click on "Next Item"

You might need to set the "media_player_path" variable to the path of the executable file of your media player.

If the media or PDF players throw an error try adding time to the "media_sleep_time" and "pdf_sleep_time" variables.


