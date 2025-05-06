from config.ignore import image_extensions, video_extensions, audio_extensions, text_extensions
def predict_name_based_on_extension(input_name, convert_type):
   #get file extension
   extension = "." + input_name.split(".")[-1]
   print(f"Input name: {input_name}")
   print(f"Extension: {extension}")
   print(f"Convert type: {convert_type}")

   # replace extension based on the conversion
   if extension in image_extensions and convert_type == "AIP":
       input_name = input_name.replace(extension, "_tiff.tiff")
   elif extension in image_extensions and convert_type == "DIP":
       input_name = input_name.replace(extension, "_jpg.jpg")
   elif extension in video_extensions and convert_type == "AIP":
       input_name = input_name.replace(extension, "_ffv1.mkv")
   elif extension in video_extensions and convert_type == "DIP":
       input_name = input_name.replace(extension, "_mp4.mp4")
   elif extension in audio_extensions and convert_type == "AIP":
       input_name = input_name.replace(extension, "_wav.wav")
   elif extension in audio_extensions and convert_type == "DIP":
       input_name = input_name.replace(extension, "_mp3.mp3")
   elif extension in text_extensions :
       input_name = input_name.replace(extension, "_pdfa.pdf")
   else:
       print("No conversion needed")

   
   return input_name