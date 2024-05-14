import logging
from pathlib import Path
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


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


def extract_model_details(model):
    # Check the type of model and extract relevant details
    if isinstance(model, MLPRegressor):
        # For MLPRegressor, extract hidden layer sizes and activation function
        hidden_layer_sizes = "_".join(map(str, model.hidden_layer_sizes))
        activation = model.activation
        return f"{hidden_layer_sizes}_{activation}"
    elif isinstance(model, RandomForestRegressor):
        # For RandomForestRegressor, extract n_estimators and max_depth
        n_estimators = model.n_estimators
        max_depth = model.max_depth or "None"  # Use 'None' if max_depth is not set
        return f"{n_estimators}_{max_depth}"
    else:
        raise ValueError("Unsupported model type")


def create_model_directory(base_dir, model, model_type):
    config_details = extract_model_details(model)
    folder_name = f"{model_type}_{config_details}"
    model_dir = Path(base_dir) / folder_name
    model_dir.mkdir(parents=True, exist_ok=True)
    logger = activate_logging(model_dir)
    return model_dir, logger
