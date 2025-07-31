"""
Icon management for services
"""
import base64
from io import BytesIO
from PIL import Image, ImageTk

# Base64 encoded icons (16x16)
ICON_DATA = {
    "default": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAEYSURBVDiNpZOxSgNBEIa/mdm53LvL3V1yMRGJSEQkIiIWFhYWFhYWFhYWPoBPYGFhYWEhCIIgCIIgCIIgGJLk7u72dmf2bSJG4y8MA8PM/3/zzwz8ZwQAIrIELAJ1oAIE/yoMwCJwE2gBNUD4DwAR6QLLQAWoAN0mi7PZLEC1tgAsichPoPIvACJSAUZA1xhTMcaYpuo0m90sy+oBQ0ADuAwMAREhIhdjjBkYYwbVajVot9tBs9kMms1m0Gw2g3a7HbTb7SCKoiCKosCyrCAMQ38X4A3Qi4hhmqZpmqZpnud5nud5nud5nud5nucqz3OV57nK8lwBcwDiLyAgxphBtVoNqtVqEEVRUK/Xg3q9HkRRFIRhGIRhGIRBEPgdgH/AZ+A7ZrQwqEacpEgAAAAASUVORK5CYII=",
    "plex": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHaSURBVDiNpZO/S1VRHMc/53zvvTc1n/pcUZRa5JBDDtHQ0NAQNDS0BQ79A0FDQ0RQU/9BRGNzS0tLNLRFQ0M0REFD5FNR8909957vt+H6Hr0+n4UHzuF8z/fz/X4/3885cMLxAJeABWAe6Ab8v4gDsADMAVPAKpCeBPjABPAJqAGVBqoBS8AEJwRGgWVjzM9YLKZ838c5RxRF7qDCMKRcLqOU2gHGTwLMAl+Louj9zMzM7fHx8a5sNktHRwftbW20tbXR0tJCEAQIIdBaU61WKZVK5PN5NjY2WF1dfQXcPwowBKy7w3p6ehKZTEb19/erwcFBdfb8eda2tvjw+QvBl03S6TRCCJRSOOdwzlEul1ldWeHRw4e8ePqUXDZLFEV3gOL/AB+YN8Z8nZ6ezoyNjQkhBPl8nsXFRV6/eYN1jnQ6jRACrTXWWqy1KKUIggDnHHfu3uXqlSt6YGDA7O3tPQMmGwGzxpjvk5OTmXQ6LT58/Mjr16959fo1xhiklCSTSZIul8PhcDgcDocLgoBYLMaFS5eQUvL06VM1Ojqq8/n8CyC3H+ABH621c7dv3268d++eiqKID58+8e7dO3K5HM45hBAIIVBKoa1Ga40Qgmwuh3OOhYUFbty8qc/19pparTbViE0Bvx9LptFD2gTzAAAAAElFTkSuQmCC",
    # Add more icons as needed
}

def get_icon(service_name):
    """Get PhotoImage icon for a service"""
    icon_key = service_name.lower().replace(" ", "_").replace("-", "_")
    
    # Get icon data
    if icon_key in ICON_DATA:
        icon_b64 = ICON_DATA[icon_key]
    else:
        icon_b64 = ICON_DATA["default"]
    
    # Convert to PhotoImage
    icon_data = base64.b64decode(icon_b64)
    image = Image.open(BytesIO(icon_data))
    return ImageTk.PhotoImage(image)
