import json

# 11. File Handling: Write output to file if allowed
def write_output_to_file(write_file: str, output_data: dict, file_format = '.py', allow_file_overwrite: bool = True, save_to_json: bool = True):
    """Write the output data to a file, allowing JSON or plain text format."""
    file_exists = False

    # Check if the file already exists
    try:
        with open(write_file):
            file_exists = True
    except FileNotFoundError:
        pass

    # Decide whether to overwrite the file or create a new one
    if (allow_file_overwrite and file_exists) or not file_exists:
        try:
            # JSON format
            if save_to_json:
                with open(write_file, mode='w' if allow_file_overwrite else 'x') as file:
                    json.dump(output_data, file, indent=4)  # Write data as JSON
            # Plain text format
            else:
                with open(f'{write_file}{file_format}', mode='w' if allow_file_overwrite else 'x') as file:
                    for key, val in output_data.items():
                        # Handle list values
                        if isinstance(val, list):
                            formatted_val = ', '.join(str(v) for v in val)
                            formatted_val = f'[{formatted_val}]'
                        else:
                            formatted_val = str(val)
                        
                        file.write(f'{key} = {formatted_val}\n')
        except FileExistsError:
            print(f"File '{write_file}' already exists. Set allow_file_overwrite to True if you want to overwrite it.")
        except IOError as e:
            print(f"Failed to write to file: {e}")
