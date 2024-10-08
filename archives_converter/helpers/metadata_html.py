import os
import json
import logging

def merge_metadata_files(destination_folder):
    root_metadata_file = os.path.join(destination_folder, "metadata.json")
    
    try:
        merged_data = {}
        files_merged = False
        files_to_delete = []
        
        for root, dirs, files in os.walk(destination_folder):
            if "metadata.json" in files:
                metadata_file_path = os.path.join(root, "metadata.json")
                relative_path = os.path.relpath(root, destination_folder)
                depth = len(relative_path.split(os.sep))
                
                try:
                    with open(metadata_file_path, 'r', encoding='utf-8') as sub_file:
                        file_content = sub_file.read()
                        cleaned_content = ''.join(char for char in file_content if ord(char) >= 32 or char in '\n\r\t')
                        sub_data = json.loads(cleaned_content)
                        if sub_data:
                            # Merge data into the appropriate level
                            current_level = merged_data
                            path_parts = relative_path.split(os.sep)
                            for part in path_parts[:-1]:
                                if part not in current_level:
                                    current_level[part] = {}
                                current_level = current_level[part]
                            current_level.update(sub_data)
                            files_merged = True
                    
                    # Mark files in deeper levels for deletion
                    if depth > 1:
                        files_to_delete.append(metadata_file_path)
                
                except json.JSONDecodeError as json_err:
                    logging.warning(f"JSON error in {metadata_file_path}: {str(json_err)}. Skipping this file.")
                except Exception as e:
                    logging.error(f"Error processing {metadata_file_path}: {str(e)}")
        
        if files_merged:
            with open(root_metadata_file, 'w', encoding='utf-8') as root_file:
                json.dump(merged_data, root_file, indent=2)
        
        # Delete metadata files in deeper levels
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
            except Exception as e:
                logging.error(f"Error deleting {file_path}: {str(e)}")
        
    except Exception as e:
        logging.error(f"Error merging and deleting metadata files: {str(e)}")

def create_metadata_html_table(destination_folder):
    try:
        metadata_file_path = os.path.join(destination_folder, "metadata.json")
        
        merged_metadata = {}
    
        for root, dirs, files in os.walk(destination_folder):
            if "metadata.json" in files:
                sub_metadata_path = os.path.join(root, "metadata.json")
                try:
                    with open(sub_metadata_path, 'r', encoding='utf-8') as f:
                        sub_metadata = json.load(f)
                    relative_path = os.path.relpath(root, destination_folder)
                    merged_metadata[relative_path] = sub_metadata
                except json.JSONDecodeError:
                    logging.warning(f"Invalid JSON in {sub_metadata_path}. Skipping this file.")
                except Exception as e:
                    logging.error(f"Error reading {sub_metadata_path}: {str(e)}")

        # If the main metadata.json exists and is not empty, merge it with the collected data
        if os.path.exists(metadata_file_path) and os.path.getsize(metadata_file_path) > 0:
            try:
                with open(metadata_file_path, 'r', encoding='utf-8') as f:
                    main_metadata = json.load(f)
                merged_metadata.update(main_metadata)
            except json.JSONDecodeError:
                logging.warning(f"Invalid JSON in main metadata file {metadata_file_path}. Skipping this file.")
            except Exception as e:
                logging.error(f"Error reading main metadata file {metadata_file_path}: {str(e)}")

        if not merged_metadata:
            logging.warning("No metadata found. Creating an empty HTML file.")

        html = """
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Metadata Overview</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }
                h2 {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                    background-color: #fff;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                    max-width: 300px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                th {
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                #searchInput {
                    width: 100%;
                    padding: 12px 20px;
                    margin: 8px 0;
                    box-sizing: border-box;
                    border: 2px solid #3498db;
                    border-radius: 4px;
                    font-size: 16px;
                }
                .metadataEntry {
                    background-color: #fff;
                    border-radius: 5px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                td:hover {
                    overflow: visible;
                    white-space: normal;
                    word-break: break-word;
                }
                .objectTable {
                    margin-bottom: 30px;
                }
                .objectTitle {
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: #2c3e50;
                }
            </style>
        </head>
        <body>
        """

        # Add search input
        html += "<input type='text' id='searchInput' onkeyup='searchMetadata()' placeholder='Search metadata...'>"
        
        html += "<div id='metadataContent'>"
        for _, files in merged_metadata.items():
            for filename, file_metadata in files.items():

                def flatten_metadata(metadata, prefix=''):
                    flattened = {}
                    for key, value in metadata.items():
                        full_key = f"{prefix}{key}"
                        if isinstance(value, dict):
                            flattened.update(flatten_metadata(value, f"{full_key}."))
                        elif not isinstance(value, (list, dict)):
                            flattened[full_key] = value
                    return flattened

                flattened_metadata = flatten_metadata(file_metadata)
                file_metadata = flattened_metadata
                for key, value in file_metadata.items():
                    html += f"<div class='metadataEntry'>"
                html += f"<h2>{os.path.basename(filename)}</h2>"
                

                objects = {}
                for key, value in file_metadata.items():
                    object_name, attr = key.split('.', 1) if '.' in key else (key, '')
                    if object_name not in objects:
                        objects[object_name] = {}
                    if attr:
                        objects[object_name][attr] = value
                    else:
                        objects[object_name] = value

                for object_name, object_data in objects.items():
                    html += f"<div class='objectTable'>"
                    html += f"<div class='objectTitle'>{object_name}</div>"
                    html += "<table>"
                    html += "<tr><th>Metadata Key</th><th>Metadata Value</th></tr>"
                    
                    if isinstance(object_data, dict):
                        for key, value in object_data.items():
                            key_parts = key.split(".")
                            attrKey = key_parts[-1] if key_parts else key
                            html += f"<tr><td>{attrKey}</td><td>{value}</td></tr>"
                    else:
                        html += f"<tr><td>{object_name}</td><td>{object_data}</td></tr>"
                    
                    html += "</table>"
                    html += "</div>"

                html += "</div>"

        html += "</div>"

        html += """
        <script>
        function searchMetadata() {
            var input, filter, metadataEntries, entry, i, txtValue;
            input = document.getElementById('searchInput');
            filter = input.value.toUpperCase();
            metadataEntries = document.getElementsByClassName('metadataEntry');

            for (i = 0; i < metadataEntries.length; i++) {
                entry = metadataEntries[i];
                txtValue = entry.textContent || entry.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    entry.style.display = "";
                } else {
                    entry.style.display = "none";
                }
            }
        }
        </script>
        """
        html += "</body></html>"
        
        output_path = os.path.join(destination_folder, "all_metadata.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        root_metadata_file = os.path.join(destination_folder, "metadata.json")
        if os.path.exists(root_metadata_file):
            try:
                os.remove(root_metadata_file)
            except Exception as e:
                logging.error(f"Error deleting root metadata file {root_metadata_file}: {str(e)}")
    except Exception as e:
        logging.error(f"Error creating HTML table from metadata: {str(e)}")
        logging.exception("Detailed traceback:")