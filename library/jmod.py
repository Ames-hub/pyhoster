import os, logging, json

class jmod:
    def getvalue(key, json_dir, default=None, dt=None):
        """
        Retrieve the value of a nested key from a JSON file or dictionary.
        Args:
            key (str): The key to retrieve in the format "parent.child1.child2[0].child3".
            json_dir (str): The file path of the JSON file to read from or write to.
            default: The default value to return if the key is not found (default=None).
            dt (dict): The dictionary to write to the JSON file if it does not exist (default=None).
        Returns:
            The value of the key if found, or the default value if not found.
        """
        # Split the key into parts (assuming key is in the format "parent.child1.child2[0].child3")
        parts = key.split('.')
        # Check if the JSON file exists
        if not os.path.exists(json_dir):
            try:
                # If not, create the parent directory if it doesn't exist
                os.makedirs(os.path.dirname(json_dir), exist_ok=True)
                if dt is not None:
                    # If dt is provided, write it to the JSON file
                    with open(json_dir, 'w') as f:
                        json.dump(dt, f, indent=4, separators=(',', ': '))
                else:
                    # Otherwise, create an empty JSON file
                    with open(json_dir, 'w') as f:
                        json.dump({}, f, indent=4, separators=(',', ': '))
            except Exception as e:
                logging.error(f"Error creating JSON file: {str(e)}")
                return default
        # Load the JSON file
        try:
            with open(json_dir, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logging.error(f"Error loading JSON file: {str(e)}")
            return default
        # Check if the JSON data is empty
        if not data:
            # If empty, fill it with an empty dictionary or the provided dt
            data = dt or {}
            try:
                with open(json_dir, 'w') as f:
                    json.dump(data, f, indent=4, separators=(',', ': '))
            except Exception as e:
                logging.error(f"Error writing to JSON file: {str(e)}")
                return default
        # Traverse the nested dictionaries/lists in the JSON data to get the value
        value = data
        for part in parts:
            if part.endswith(']'):  # Check if part is an array index
                index = int(part[part.index('[') + 1:part.index(']')])  # Extract the array index
                value = value[index]
            else:
                if part in value:
                    value = value[part]
                else:
                    # If the key doesn't exist, return the default value (default=None)
                    return default
        return value

    def setvalue(key, json_dir, value, default=None, dt=None):
        # Check if the file at json_dir exists
        if not os.path.exists(json_dir):
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(json_dir), exist_ok=True)
            
            # Create and fill the JSON file with dt if provided
            if dt is not None:
                with open(json_dir, 'w') as file:
                    json.dump(dt, file, indent=4, separators=(',', ': '))
            elif default is not None:
                with open(json_dir, 'w') as file:
                    json.dump(default, file, indent=4, separators=(',', ': '))
        
        try:
            with open(json_dir, 'r+') as file:
                data = json.load(file)
                keys = key.split('.')
                
                # Traverse the nested structure to access the key
                nested_data = data
                for nested_key in keys[:-1]:
                    nested_data = nested_data.setdefault(nested_key, {})
                
                # Set the value of the selected key
                nested_data[keys[-1]] = value
                
                # Move the file pointer to the beginning and rewrite the JSON data
                file.seek(0)
                json.dump(data, file, indent=4, separators=(',', ': '))
                file.truncate()
                
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            return default
        
        return value

    def addvalue(key, json_dir, value, default=None, dt=None):
        """
        Add a value to a list in a nested key of a JSON file or dictionary.
        Args:
            key (str): The key to add to in the format "parent.child1.child2[0].child3".
            json_dir (str): The file path of the JSON file to read from or write to.
            value: The value to add to the list.
            default: The default value to return if the key is not found (default=None).
            dt (dict): The dictionary to compare against the JSON file and create missing keys (default=None).
        Returns:
            The updated value of the key if added successfully, or the default value if not found.
        """
        parts = key.split('.')
        if not os.path.exists(json_dir):
            try:
                os.makedirs(os.path.dirname(json_dir), exist_ok=True)
                if dt is not None:
                    with open(json_dir, 'w') as f:
                        json.dump(dt, f, indent=4, separators=(',', ': '))
                else:
                    with open(json_dir, 'w') as f:
                        json.dump({}, f, indent=4, separators=(',', ': '))
            except Exception as e:
                logging.error(f"Error creating JSON file: {str(e)}")
                return default
        try:
            with open(json_dir, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logging.error(f"Error loading JSON file: {str(e)}")
            return default
        if not data:
            data = dt or {}
            try:
                with open(json_dir, 'w') as f:
                    json.dump(data, f, indent=4, separators=(',', ': '))
            except Exception as e:
                logging.error(f"Error writing to JSON file: {str(e)}")
                return default
        
        # Compare dt with the JSON data and create any missing keys
        def compare_and_create_keys(parts, data, dt):
            if len(parts) == 1:
                key = parts[0]
                if key.endswith(']'):
                    index = int(key[key.index('[') + 1:key.index(']')])
                    if not isinstance(data[index], list):
                        data[index] = [data[index]]
                else:
                    if key not in data:
                        data[key] = dt[key]
                        return
            else:
                key = parts[0]
                if key.endswith(']'):
                    index = int(key[key.index('[') + 1:key.index(']')])
                    if not isinstance(data[index], list):
                        data[index] = [data[index]]
                    compare_and_create_keys(parts[1:], data[index], dt)
                else:
                    if key not in data:
                        data[key] = dt[key] if key in dt else {}
                    compare_and_create_keys(parts[1:], data[key], dt)
        
        if dt is not None:
            compare_and_create_keys(parts, data, dt)

        # Define a recursive function to traverse the nested dictionaries/lists in the JSON data
        def _addvalue(parts, value, data):
            if len(parts) == 1:
                key = parts[0]
                if key.endswith(']'):
                    index = int(key[key.index('[') + 1:key.index(']')])
                    if not isinstance(data[index], list):
                        data[index] = [data[index]]
                    data[index].append(value)
                else:
                    if not isinstance(data[key], list):
                        data[key] = [data[key]]
                    data[key].append(value)
            else:
                key = parts[0]
                if key.endswith(']'):
                    index = int(key[key.index('[') + 1:key.index(']')])
                    if isinstance(data[key], list):
                        data[key].append(value)
                else:
                    key = parts[0]
                    if key.endswith(']'):
                        index = int(key[key.index('[') + 1:key.index(']')])
                        if isinstance(data[index], list):
                            _addvalue(parts[1:], value, data[index])
                    else:
                        if key in data:
                            _addvalue(parts[1:], value, data[key])

        try:
            _addvalue(parts, value, data)
        except Exception as e:
            logging.error(f"Error adding value to JSON file: {str(e)}")
            return default
        
        try:
            with open(json_dir, 'w') as f:
                json.dump(data, f, indent=4, separators=(',', ': '))
        except Exception as e:
            logging.error(f"Error writing to JSON file: {str(e)}")
            return default

        return data

    def remvalue(key, json_dir, value, default=None, dt=None):
        """
        Remove a value from a list in a nested key of a JSON file or dictionary.
        Args:
            key (str): The key to remove from in the format "parent.child1.child2[0].child3".
            json_dir (str): The file path of the JSON file to read from or write to.
            value: The value to remove from the list.
            default: The default value to return if the key is not found (default=None).
            dt (dict): The dictionary to compare against the JSON file and create missing keys (default=None).
        Returns:
            The updated value of the key if removed successfully, or the default value if not found.
        """
        parts = key.split('.')
        if not os.path.exists(json_dir):
            try:
                os.makedirs(os.path.dirname(json_dir), exist_ok=True)
                if dt is not None:
                    with open(json_dir, 'w') as f:
                        json.dump(dt, f, indent=4, separators=(',', ': '))
                else:
                    with open(json_dir, 'w') as f:
                        json.dump({}, f, indent=4, separators=(',', ': '))
            except Exception as e:
                logging.error(f"Error creating JSON file: {str(e)}")
                return default
        try:
            with open(json_dir, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logging.error(f"Error loading JSON file: {str(e)}")
            return default
        if not data:
            data = dt or {}
            try:
                with open(json_dir, 'w') as f:
                    json.dump(data, f, indent=4, separators=(',', ': '))
            except Exception as e:
                logging.error(f"Error writing to JSON file: {str(e)}")
                return default
        
        # Compare dt with the JSON data and create any missing keys
        def compare_and_create_keys(parts, data, dt):
            if len(parts) == 1:
                key = parts[0]
                if key.endswith(']'):
                    index = int(key[key.index('[') + 1:key.index(']')])
                    if not isinstance(data[index], list):
                        data[index] = [data[index]]
                else:
                    if key not in data:
                        data[key] = dt[key]
                        return
            else:
                key = parts[0]
                if key.endswith(']'):
                    index = int(key[key.index('[') + 1:key.index(']')])
                    if not isinstance(data[index], list):
                        data[index] = [data[index]]
                    compare_and_create_keys(parts[1:], data[index], dt)
                else:
                    if key not in data:
                        data[key] = dt[key] if key in dt else {}
                    compare_and_create_keys(parts[1:], data[key], dt)
        
        if dt is not None:
            compare_and_create_keys(parts, data, dt)

        # Define a recursive function to traverse the nested dictionaries/lists in the JSON data
        def _remvalue(parts, value, data):
            if len(parts) == 1:
                key = parts[0]
                if key.endswith(']'):
                    index = int(key[key.index('[') + 1:key.index(']')])
                    if isinstance(data[index], list):
                        if value in data[index]:
                            data[index].remove(value)
                else:
                    if isinstance(data[key], list):
                        if value in data[key]:
                            data[key].remove(value)
            else:
                key = parts[0]
                if key.endswith(']'):
                    index = int(key[key.index('[') + 1:key.index(']')])
                    ###
                    if isinstance(data[key], list):
                        if value in data[key]:
                            data[key].remove(value)
                else:
                    key = parts[0]
                    if key.endswith(']'):
                        index = int(key[key.index('[') + 1:key.index(']')])
                        if isinstance(data[index], list):
                            _remvalue(parts[1:], value, data[index])
                    else:
                        if key in data:
                            _remvalue(parts[1:], value, data[key])

        try:
            _remvalue(parts, value, data)
        except Exception as e:
            logging.error(f"Error removing value from JSON file: {str(e)}")
            return default

        try:
            with open(json_dir, 'w') as f:
                json.dump(data, f, indent=4, separators=(',', ': '))
        except Exception as e:
            logging.error(f"Error writing to JSON file: {str(e)}")
            return default

        return True