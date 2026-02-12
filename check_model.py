import h5py
import json

try:
    print("Examining pneumonia_classification_model.h5...")
    with h5py.File('pneumonia_classification_model.h5', 'r') as f:
        print("HDF5 file opened successfully")
        print("\nFile structure:")
        def print_structure(name, obj):
            print(f"  {name}")
        f.visititems(print_structure)

        # Check model_config
        if 'model_config' in f.attrs:
            print("\nModel config found:")
            config = json.loads(f.attrs['model_config'])
            print("Config keys:", list(config.keys()))

            # Check for batch_shape
            def find_batch_shape(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        if key == 'batch_shape':
                            print(f"Found batch_shape at: {current_path} = {value}")
                        find_batch_shape(value, current_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        find_batch_shape(item, f"{path}[{i}]")

            find_batch_shape(config)

            # Check for DTypePolicy
            def find_dtype_policy(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        if key == 'dtype_policy' and value == 'DTypePolicy':
                            print(f"Found DTypePolicy at: {current_path} = {value}")
                        find_dtype_policy(value, current_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        find_dtype_policy(item, f"{path}[{i}]")

            find_dtype_policy(config)

        # Check model_weights
        if 'model_weights' in f:
            print(f"\nModel weights found with {len(list(f['model_weights'].keys()))} groups")

        print("\nFile appears to be a valid HDF5 Keras model file")

except Exception as e:
    print(f"Error examining model file: {e}")
    print("The file may be corrupted or not a valid HDF5 file")
