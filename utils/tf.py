#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import sys
import logging
from pathlib import Path
from tensorflow.keras.layers import LSTM, Dense, TimeDistributed
from context import data_dir


def activate_logging(model_directory):
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler for the log file
    log_file = str(model_directory / "log.txt")

    # Clear the log file if it exists
    if Path(log_file).exists():
        Path(log_file).unlink()

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create a formatter and add it to the file handler
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)
    return logger


# Helper function to extract model layer details
def extract_model_details(model):
    details = []
    for layer in model.layers:
        if isinstance(layer, LSTM):
            details.append(f"{layer.units}U-LSTM")
        elif isinstance(layer, Dense):
            details.append(f"{layer.units}U-Dense")
        elif isinstance(layer, TimeDistributed):
            # Check what type of layer is wrapped by TimeDistributed
            wrapped_layer = layer.layer
            if isinstance(wrapped_layer, Dense):
                details.append(
                    f"TD-{wrapped_layer.units}U-Dense-{wrapped_layer.activation.__name__}"
                )
            else:
                details.append("TD-OtherLayer")
    return "_".join(details)


# Helper function to create a directory based on model configuration
def create_model_directory(base_dir, model, model_type):
    config_details = extract_model_details(model)
    folder_name = f"{model_type}_{config_details}"
    model_dir = Path(base_dir) / folder_name
    model_dir.mkdir(parents=True, exist_ok=True)
    logger = activate_logging(model_dir)
    return model_dir, logger
