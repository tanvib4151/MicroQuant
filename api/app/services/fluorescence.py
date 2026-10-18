from .image_loader import InputError

def channels_for(values):
    return ["gray"] if values.ndim == 2 else ["red", "green", "blue"]

def extract_channel(values, channel):
    available = channels_for(values)
    if channel == "auto":
        channel = "gray" if values.ndim == 2 else "green"
    if channel not in available:
        raise InputError("Selected channel is unavailable for this image.")
    return (values if channel == "gray" else values[:, :, available.index(channel)]), channel
