import os
import yaml
import logging

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

def create_metadata_html_table(destination_folder):
    try:
        merged_metadata = {}
        for root, dirs, files in os.walk(destination_folder):
            if 'metadata.yaml' in files:
                metadata_file_path = os.path.join(root, 'metadata.yaml')
                with open(metadata_file_path, 'r') as f:
                    metadata = yaml.safe_load(f)
                    if metadata:
                        merged_metadata.update(metadata)
        
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
            </style>
        </head>
        <body>
        """

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