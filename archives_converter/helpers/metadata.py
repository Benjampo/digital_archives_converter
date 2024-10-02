import os
import stat
import pwd
import grp
from datetime import datetime
from rich import print
import subprocess
import logging
import yaml


def create_metadata_files(destination_folder):

    for item in os.listdir(destination_folder):
        item_path = os.path.join(destination_folder, item)
        if os.path.isdir(item_path):
            metadata_file_name = "metadata.yaml"
            metadata_file_path = os.path.join(item_path, metadata_file_name)
            
            with open(metadata_file_path, "w") as metadata_file:
                yaml.dump({}, metadata_file)

            print(f"Empty metadata file created: {metadata_file_path}")

def extract_metadata(file_path):

    if os.path.basename(file_path) == "metadata.yaml":
        return ""

    try:
        exiftool_command = [
            'exiftool',
            file_path
        ]
        result = subprocess.run(exiftool_command, capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        logging.error(f"Error extracting metadata from {file_path}: {str(e)}")
        return ""


def append_metadata(metadata, metadata_file, original_file_path):
    try:
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)

        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                existing_data = yaml.safe_load(f) or {}
        else:
            existing_data = {}

        metadata_dict = {}
        for line in metadata.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)

                value = value.strip().strip('"\'')

                value = value.replace('\n', ' ')
                metadata_dict[key.strip()] = value

        file_key = os.path.basename(original_file_path)
        existing_data[file_key] = {
            'metadata': metadata_dict,
            'timestamp': datetime.now().isoformat()
        }

        with open(metadata_file, 'w') as f:
            yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)

    except Exception as e:
        logging.error(f"Error appending metadata for {original_file_path} to {metadata_file}: {str(e)}")

def merge_metadata_files(destination_folder):
    root_metadata_file = os.path.join(destination_folder, "metadata.yaml")
    
    try:
        merged_data = {}
        for root, dirs, files in os.walk(destination_folder):
            if "metadata.yaml" in files:
                metadata_file_path = os.path.join(root, "metadata.yaml")
                if metadata_file_path != root_metadata_file:
                    with open(metadata_file_path, 'r') as sub_file:
                        sub_data = yaml.safe_load(sub_file)
                        if sub_data:
                            merged_data.update(sub_data)
                    
                    os.remove(metadata_file_path)
                    print(f"Removed: {metadata_file_path}")
        
        with open(root_metadata_file, 'w') as root_file:
            yaml.dump(merged_data, root_file, default_flow_style=False, sort_keys=False)
        
        print(f"Merged metadata files into: {root_metadata_file}")
    except Exception as e:
        logging.error(f"Error merging metadata files: {str(e)}")

def metadata_to_html_table(destination_folder):
    try:
        merged_metadata = {}
        for root, dirs, files in os.walk(destination_folder):
            if 'metadata.yaml' in files:
                metadata_file_path = os.path.join(root, 'metadata.yaml')
                with open(metadata_file_path, 'r') as f:
                    metadata = yaml.safe_load(f)
                    if metadata:
                        merged_metadata.update(metadata)
        
        html = "<html><head><style>"
        html += "table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }"
        html += "th, td { border: 1px solid black; padding: 8px; text-align: left; }"
        html += "th { background-color: #f2f2f2; }"
        html += "h2 { margin-top: 30px; }"
        html += "#searchInput { width: 100%; padding: 12px 20px; margin: 8px 0; box-sizing: border-box; }"
        html += "</style></head><body>"

        # Add search input
        html += "<input type='text' id='searchInput' onkeyup='searchMetadata()' placeholder='Search metadata...'>"
        
        html += "<div id='metadataContent'>"
        for file_name, file_data in merged_metadata.items():
            file_metadata = file_data.get('metadata', {})
            timestamp = file_data.get('timestamp', '')
            
            html += f"<div class='metadataEntry'>"
            html += f"<h2>{file_name}</h2>"
            html += f"<p>Timestamp: {timestamp}</p>"
            html += "<table>"
            html += "<tr><th>Metadata Key</th><th>Metadata Value</th></tr>"
            
            for key, value in file_metadata.items():
                html += f"<tr><td>{key}</td><td>{value}</td></tr>"
            
            html += "</table>"
            html += "</div>"
        
        html += "</div>"

        # Add JavaScript for search functionality
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
        with open(output_path, 'w') as f:
            f.write(html)
        
        print(f"HTML table with all metadata created: {output_path}")
    except Exception as e:
        logging.error(f"Error creating HTML table from metadata: {str(e)}")
