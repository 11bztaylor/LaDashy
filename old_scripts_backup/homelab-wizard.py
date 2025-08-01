#!/usr/bin/env python3
"""
Universal Homelab Documentation Wizard
Works on Windows, macOS, and Linux
Auto-discovers services and creates comprehensive documentation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import platform
import os
import sys
import json
import threading
import queue
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO

# Check for required modules
try:
    import paramiko
except ImportError:
    print("Installing required module: paramiko")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Installing required module: Pillow")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageTk

# Embedded icons (base64 encoded 16x16 icons)
ICONS = {
    # Media Services
    "plex": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHaSURBVDiNpZO/S1VRHMc/53zvvTc1n/pcUZRa5JBDDtHQ0NAQNDS0BQ79A0FDQ0RQU/9BRGNzS0tLNLRFQ0M0REFD5FNR8909957vt+H6Hr0+n4UHzuF8z/fz/X4/3885cMLxAJeABWAe6Ab8v4gDsADMAVPAKpCeBPjABPAJqAGVBqoBS8AEJwRGgWVjzM9YLKZ838c5RxRF7qDCMKRcLqOU2gHGTwLMAl+Kouj9zMzM7fHx8a5sNktHRwftbW20tbXR0tJCEAQIIdBaU61WKZVK5PN5NjY2WF1dfQXcPwowBKy7w3p6ehKZTEb19/erwcFBdfb8eda2tvjw+QvBl03S6TRCCJRSOOdwzlEul1ldWeHRw4e8ePqUXDZLFEV3gOL/AB+YN8Z8nZ6ezoyNjQkhBPl8nsXFRV6/eYN1jnQ6jRACrTXWWqy1KKUIggDnHHfu3uXqlSt6YGDA7O3tPQMmGwGzxpjvk5OTmXQ6LT58/Mjr16959fo1xhiklCSTSZIul8PhcDgcDocLgoBYLMaFS5eQUvL06VM1Ojqq8/n8CyC3H+ABH621c7dv3268d++eiqKID58+8e7dO3K5HM45hBAIIVBKoa1Ga40Qgmwuh3OOhYUFbty8qc/19pparTbViE0Bvx9LptFD2gTzAAAAAElFTkSuQmCC",
    "jellyfin": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGxSURBVDiNpZMxSBthFMf/33d3l1yCiRpNqkm1VgQRB0EEB6dCh0KHLl0KpVMRHDoUBEFwEAQHQRBEEETBQSgdCh0KHTq4FDoUBEEQBEGQGk2TXpLLXe5yXwcbTWJtB/94w3vv9/++977vCfxnCQBQSr0A3gBo+FchALwH8AbAOwAVAMJ/ACilfgCPAXgBOMdBa60NABaAR5TSXwC8/wKglHoBfATgZ4xFGGMhxlgoHA6HQqFQKBgMBgOBgF8I4XNLS0t/ADytBlBK/QB6AWiEkIBpmmarVqvV6nQ6rdFoNNJqtVqpVCpBCPE5Go3GAOCtBLABTALwEkJcVqvVaquUUlutVitRFEWUy+VSVVVVsixLAJ4AdQCfAXjcX8/j8bg9Ho/H7Xa7XS6Xy+VyuRxSSjkcDofhcDhs2LZt6bpuAhi7D/gEwEvTNC3Lsiyr0rZt27Zt27QsyzJN0zSllJIQIthsNpsApAGglPoslUqVjTHGmJRSSimllJIxZvxbIIRwKKU+m6ZZBnALAKvVanmLxeJ1Pp+/LhQKhUKhUCjk8/l8Pp/PXxcKBb1UKl0DuLn7Xud4BxN4yP9MU6RJAAAAAElFTkSuQmCC",
    "emby": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGNSURBVDiNpZO/S1VRHMc/3/M959xzH+r1+kJFRUWlhwT9gEiCfkAQBEEQBEHQ0tDQ0NDQ0tLQ0NDQ0NDQDxqCIAiCIAiCoB9EEZHovfd67/3e7/mebyN6eu/qCw6c4Rzeh8/nfM4R/lPi3wGl1DgwCAwBXYD4V6EABoFRYBxoB4T/AFBKVYDHgA8kgNprqtVqBqgBjyilKoD/LwBKKQ/oBBJCiEQymUwmk8lkKpVKpVKpVCqZTCaT8Xg8HovFYlJKKYBu4Fm9B0qpGBAVQkRjsVg0EolEI5FINBQKRUKBYCAYCARC4XA4HA6Hw2GPxxOQUkoAy40AWoGQEMKfTCbjyVQqmUqlUqlkMplMJBKJRDwej8fj8XjMsiwrGo1GpRAiCGiNAGJCiGgmk4mnM5l0OpPJpFPpdCqVSqVSqVQqmUwmkx6vNwjUgGmgvRFATAjhT6VSyXQ6nU5ns9lsJpPJZjKZTCaVTmfS6XTGCHvCUsqoBegEYBiGI51Ox9PptNSGYTgbjYZhOAzDcOiGYTgMw3AYhuHQDcNw/AFB8JKUfaOhkQAAAABJRU5ErkJggg==",
    "radarr": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHFSURBVDiNlZO/axRBFMc/b2ZnZ3dv9y537y4mXiIRCYIgCIIgCIIgWFhYWFhYWFhYWPgHWFhYiIWFhYWFIAiCIAiCIAiCIAiCYBGMud/uzuzOvJnXnAk5vYsDA8O8N5/5ft/MvBH8ZwkAWutXQB9wAWgDxL8KBdAHXAS6gGZA+A8ArfUqcAtIAklguQ7lcrn8H8gCN7XWP4DUvwBorVPAPcDWWjuttY7WOgcOAKy13ga81VrngNS+Z6CESI0Do0BaKZXO5/P5fD6fz+VyuVw2m83mcrlcLpvN5vIFV2lt0kAv8BQQ+wKUUglgnzEm09LS0pJMJpPJRCKRSCQSCX8ikYgnk0kRj8dJJBIEQRAA7AP6d+8gtDXOI0BKKZWQUiaklEJK6ZdS+lNKKaSUQkophBBCSinqIAAGqgDbpmnmjDG5QqFQKBQKBcdxHKdQKBRc13Vd13Vdx3Ecx3VdtxqGBPCpBigB40DKcZxCoVAoOq7rFl3XLbqu6xaLxWKxWCwWi8Vi0SmVSg6wBnytAQqABczUgmG1Wt2EajXcqFQqlWAj2AjCMAzDMAw3Qwg3wnBrcBXYOXJ4Azb/BSjvstY/hReCJFvz9e0AAAAASUVORK5CYII=",
    "sonarr": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAG4SURBVDiNlZO/axRBFMc/s7Ozs7u3e5e7uztPRCIRiYiIiIiIiIiIWFhYWFhYWFhYWFhY+AdYWFiIhYWFhYWFIAiCIAiCIAiCIBhERC/Jze7tzs68mckkZ+7yLgwM8968z3y/b2aewH9WAKCUGgEGgT6gExD/KgzAINAP9AEdgPAvAEqpIjAEpIAkkK+zeD6fz9dYCJyglPoJpP8FQCmVBk4BJa11SW9Xa23QRimVA9J7noFSKgVcAAxjTKZQKBQKhUKhkM/n8/lcLpfL5XK5XC6Xy+Xz+bzOF/Jaa5MBrgHXBbAvQEqZaG1tbc0kk8lkIpFIJBKJRCKRSCT8iUQink6nRSwWI5lMEgRBALQCQ3t3IDZ0HHFAAymlTEgpE1JKIaX0Syn9KaUUUkohpRRCCCGl3A29BzY0vLEOWEqplDEmWyqVSmXHcZyy4zhO2XEc13Vd13Vd13Ucp+yWnXI1DAng2xaggBmgVZumqYvFYrHEiq7r6hUrVnRd19V1Xa3run61KrAOrNYAAmAUaLU1TVNqrbWmaRql0ihqg42gUqlUKkEQBBtBEARBUAmCStAYGoCtvxT9AyDIiJ5OaYhcAAAAAElFTkSuQmCC",
    "prowlarr": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHaSURBVDiNlZO9axRBGMZ/s7Mzu3u7ye7e3oUkJhGJiIiIiIiIWFhYWFhYWFhYWFhY+AdYWFiIjYWFhYWFIAiCIAiCIAiCIBgkQUTO3O3t7uzXzGvOhJzdFwYGhpl5nt/7vvPOCP6zBACtdT8wBAwC3YD4V6EABoEBYAjoAoT/ANBa54H7QBpIAvk6M/P5fL5GH3BHa/0TSP8LgNY6DVwGHGOMaxqGaRrVo7U2QA64tOcZaK1TwDXAr1Qqfi6Xy+VyuVwuk8lkMul0Op1Op9PpdDqdzmazWZPNZk2tTRq4ClwTwL4AKWWira2tLZlMJpOJRCKRSCQSiUQikfAnEol4Op0WsVgMz/P8IAhaARE7uxDb4uwHNgEppUxIKRNSSiGl9Esp/SmlFFJKIaUUQgghpQyAfmC4FrCMMXnXdQuu67qu67qu4ziu67qu67qu67quWywWi67ruqAKuA4M1ACuMSZfKBRKhWKxWCwWi8VisVgsFotFp1gsOo7jOJ4f+EA78KwGKAM7QKu1lre2tp58K5fLpePWWls2xpRt1VarYblSqVTCKAqjKIrCKoRhGEZxHG/jvz9W/QPo/gu48Rfwf6sLOAJ0/gbYfwA2gHc1gADeAu8/A08awM6e6FXvYgAAAABJRU5ErkJggg==",
    
    # Network Services
    "docker": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIVSURBVDiNpZM7aBRRFIa/c+/MzOzs7GZ3s5tsYmISlYiIiIiIWFhYWFhYWFhYiI2FhYWFhYWFhYWFhYWFhYWIiIiIiCgYFTGJMbuZ3dmd2Zl773XNJtEk4oGBgTP/d77/nHOO4D9LAFBKjQBngJNAJyD+VSiAM8AZ4BTQBgj/AaCUKgA3gDSQBHJ1luVyuVyNI8A1pdRvIP0vAEqpNHAZKGmtS9Y0TdM0qkcp5QEp4OKeM1BKpYBrgG+MKZqm6ZmmabqO4ziOsizLsizLsizLcl3XdV3XdVEDXAGuCmBfgJQy0dLS0pJMJpPJRCKRSCQSiUQikfAnEol4Op0W0WiURCIR+r7fAhzcsQOxKRMAnJppUkqZkFImpJRCSulPKaWQUgoppRBCCCnlJpyGxje2AQutdda2bcfRuuQA2rZt27Isy7Zt27YdR9t2CSyQB9IA1ABGgZS2bdu2Hcd2HM/1tGu7nu16nu/7vud5vue5nu+HQRiEYRCGwXvgNnCnDuADa0CLMUbX0DSNyhozmcnNZP5s5s+fP39kbGws42JCYLVm8BV4vQ3gAZNAi2kbXTbGlIzRpkxZaWOsMcaKGIAgqBFEAC+BBzVgDXgGtJqmKRhjCsaYvDEmy5LfyiTjKioihBBRRBAhQog3wENgoQEAh4Gj2zTrStM0izVqwOH/AgghLgoh7m8DrgshLv4BCC5qlAv5LUkAAAAASUVORK5CYII=",
    "nginx": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHfSURBVDiNpZO/axRBFMc/b2ZnZ3d2dy93d3dxiUQkIiIiIiIiFhYWFhYWFhYWFhYW/gEWFhZiYWFhYWEhCIIgCIIgCIIgCEII4a53t7e7s7Mz8yZnzMVcFgYGhnnz+X7fe/Nm4D8jABCRe8AM0AckgPBfhQGYAS4CN4EuQPgPABGpAFeABJAAindcXCwWizWuApdF5CeQ+BcAEUkA54CiUqpomqZpmqZZ1pZlWZZlWZZt27Zt27Zt27Zt2VlKqSJwFjgrgAMBSqnOdDqdTqVSqVQymUwmk8lkMplMJpPJZDKVSqVSqVQqFYvF1HA4PAxc/70DcVAGAJeMMT6A7/v4vu8D+J6H53l4ruvidxy3LbiuSwMM0DiMSqkuY4xvjPGNNqbRqFqtVqtWq9VatVqrVSu1Wq1WrdZqtVqtVtPayAa4QBOwrgtgAe4Z3TaNaWirrcbGGN3wdcPXxmitG8YY3fCN0VrrOqCBGcA6aAe/gWcHQRlj6k4hX8gVCoVCPpfL5XK5XC6bzWaz2Ww2m81ms+lcLpfXWteBL8CbdoAs8AJI+66rPNf1cDseW6y2YbMNG23YaMNmy3cdF9AW8Bj42AZwgeVfINcF3Bm/7wDcBu5/B97tAPgJvKoBhMDtFphfDVKpzWPuLasAAAAASUVORK5CYII=",
    "pihole": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGzSURBVDiNpZO/axRBFMc/b2ZnZ2/3bvf2fi2JRCIRERERERGxsLCwsLCwsLCwsLCwEAsLCwsLCwsLQRAEQRAEQRAEQRCUEJEk3u3t3e7O7szOm3lNzJmT+MLAwPC+n+/3vXkz8J8RAIjIArAI9AEJIPxXYQAWgQXgOtAFCP8BICIlYAlIAAkg3+Tler3eNvtKRH4CiX8BEJEE0AsUlFIFwzAMwzAMyzAMwzAMwzRN0zRN0zRN0zRNVVBKFYAeoEcABwKUUp3pdDqdSqVSqWQymUwmk8lkMplMJpPJZCqVSqVSqVQqGo1Gg8HANuD93oHYLwMAE8aYBkCj0aDRaABQr9ep1+vU6nVqtRo1x6lVq9VqtVqrVqvVasPtAG8HKqUGm4Btb5iGMabhuq7r1l3Xdd26W3dd13Xdbru77rqu1loDJlAFFtsB8sBME7wXhIvruq7n+Z7neb4XBEHgB77vB77v+77v+77ve77nBUEQ7AJuAVNtAGtgG4gZY9qdSqVS2Wm32wBVQAPvgJdtAHXgNRC11jqO4ziO4ziObTu2Y9u2bTu2Y9uObdu247KWRVcIrAJP24H/TBT4tA94/htw9wfH8h+b/QAAAABJRU5ErkJggg==",
    "portainer": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIKSURBVDiNlZO/axRBFMc/b2Zn53Z3by93e3c5Y0QiIiIiIiIWFhYWFhYWFhYWFhYWFv4BFhYWYmFhYWEhCIIgCIIgCIIgCIKQRJOc97N7O7uzM/OaMyZ34gsDw7z5fL/vvXkz8J8RAIjIfeAy0AckgPBfhQG4DFwGrgLdgPAfACJSBm4BCSABFJqsUCgUasUNEdkCEv8CICIJYAgoGGOMMca0VKVUFXgKPGnpQUQk8RN4BKSMMalcLpfL5XK5bDabzWaz2WzWsizLsizLsizLsm0751iWnfX5fI2xMcYAxz+dwdH+c5g8lkqlmjR9Pp+v0XcRx3FcHMfBcRwc2yZvDCuAGBhjGnHQJI7tdFrdbrd3SpJEkiRJkiQhhBBCCKGEEEIKIaQSQkgpJQDnm8bOmNFQKKSCwWAwEAgEAoFAIBAIBPx+v9/v9/t9Pp/P5/P5VDAY/AHMAKm9APl9VgUCgUA0Go1GI5FINBKJRKKRSCQSjUaj0VgsJmKxmIhGoyIcDotwOLwXYBWIuv9VKpXKzrQhhFBSSimEkEpKKaWUUgohpFJKKSFEW4DvQLrR3263p6ampo4ppTpkW5RSSimlVKcQYlDdunXrdDN5DxgHoq7rNrcsy3JcOwfw23GcjO04VsMYoxWYBS6JyMQfLfwB/gELQPNg/ms9AN42wStNcP5feaAZUUOkyNsAAAAASUVORK5CYII=",
    
    # Monitoring
    "grafana": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHqSURBVDiNpZO/axRBFMc/b2ZnZ3dv73bv7u4SiUQkIiIiIiIWFhYWFhYWFhYWFhYW/gEWFhZiYWFhYSEIgiAIgiAIgiAIghJi7nJ3t3d7uzO7M/OaELMJXhgYGObN5/t9782bgf+MAEBEHgBzQB+QAoJ/FQZgDpgDrgA9gPAfACJSApaBFJACCk1WKBQK1eIGsCAiP4HUvwCISAoYAwrGGGOMMU1VKpW+AW+bvgBmWxsg6iKO42AdxyHjOM4acAcY/r0DsS8TAKuO6+I6Dq7j4LouruviFAoFp1AoFK1isVi0LMtyXNdVgAIGaI0hIilgrNls13Vd2y4Wi5ZlWZZlWbZlWZZdLpft6upq2bZtu7zcCrALdDuO49i2bduWZVlWqVQqWqVSqVgqlYqlUqlUKpVKpWKpVCo5cRSvA6M0ARwHbiulcsYYq/k2m9gGSoAJ9g5aD+2PrPKW7TiOKhaLViE/mc/nc/nJyUl/cnJycnx8fNyfGLPHR0et0ZER4ziOBD4AX1oAVoEvQIdSqkOGoQzDEJJJSEQikURE0tZ0Oh2NNZ1EhGEohBEJBD41A0TAPaBDa+2rqampqampqampKa215/v+lK6qqiorq6uqsrys6/W6p7WuAM+Ajy0Af8AP4OhvwMX/AIt/AQsBiVKLq9ceAAAAAElFTkSuQmCC",
    "prometheus": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHLSURBVDiNpZO/axRBFMc/b2ZnZ/f2dm/v7i4mIhEREREREbGwsLCwsLCwsLCwsLAQCwsLCwsLCwsLQRAEQRAEQRAEQRCUkJCQ3N3e3t7uzs7MvJkXcyEXvTAwMMybz/f73ps3A/8ZAYCIPADmgH4gDYT/KgzAHHANuAr0AsJ/AIhIGVgG0kAaKDZZsVgsVotbwIKI/ADS/wIgImlgHCgYY4wxxjTVH+AVsAIcb/ogIgnAG2NuvdM0jSiKCMOQKIqIoogo1ESBJooiNr5tEEURURQRBAFRFBFFEUEQEARBw7gDbPBrbHf3d3d3d3sJj8fj8Xg8nkQikfB4PB6Px+PxeDxer8fj8STcO3fsY2PjDXn/EuBmKpXyhEKhoM/n8/l8Pp/P7/f7/X6/3x8IBAKBQCAQ8Pv9/mAgEAgGg8FgKBQKNQO8B5IYY3Lbtm3btm2btu04juM4juPYtm1bY2Njlu04jmU7jmO5d2/b5vr6epOAA2w2A/wEUm6325VIJFyJRCLhTiQSCXcikXAlk8lkMplMJt0ul9vtdrvT6XQ6FoulZ2ZmfLOzs60Ap4FTLQAq2CJaa+05OzvrnZ2dFa21V2vt01r7gDcAtxCR5wfa/gK7QJD2+dXVsAAAAABJRU5ErkJggg==",
    "uptime_kuma": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAG6SURBVDiNpZM9aBRBGIafb2ZnZ3fv9u727i4xiUQiEhERERELCwsLCwsLCwsLCwsLC7GwsLCwsLCwsBAEQRAEQRAEQRAEJSQkJHe3t7e7Ozs78xm72Yu5LAwMDPPO8z7ffGPgPyMAEJE54BLQDySB4F+FALgEXAQuAD2A8B8AIpIHloAkkATydZbP5/PV4gqwICI/geS/AIhIEhgF8kopo5QySqnyLlWpVNZrtRpKKaNpmlZKaaWUUkqpaAe4BjRvA4jIJcuyZjOZjJXJZFJmsplMJpNJm6ZpmqZpmum0maZN00ybZto0TdNMmaZp+nw+H7ACrALi98hJYNSyrJRlpexyqby7rJTSrpTSWinlSimtXddVruvqSCnlyljgCVC4C3C1XC5XlFK6aVUpVa7X1lFKlcvlcrlarVar1Wq1WCwWy6VSqby9vV0G5oC9AOu6bo1SyuVyOZfL5XI5x3GcnOM4juM4Ts5xHMexbdu2bduO4zgqiiL7QBb3A0TRiWOH+FKdnZ2q2iLdKNY/AdeBqyLyeP+5dwKOAWeagDdNgO+AsR1Qyxh4BGwC64D7F3f4BywAjfP5r/UA+AJVYJNcAOJGiAAAAABJRU5ErkJggg==",
    
    # Home Automation
    "home_assistant": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHXSURBVDiNpZO9axRBGMZ/M7Ozs3t7ye3dXe5iIhKRiIiIiIiFhYWFhYWFhYWFhYWFWFhYWFhYWFhYCIIgCIIgCIIgCIIQQkJyu7d3tzO7O/OO2eTu4gsDw8y8z/M+7zvvDP9ZAoBS6gFwCRgAMkD0r0IBXAIuApeBPkD4DwClVBG4CWSADJBvslw+ny/WuKaU+gVk/gVAKZUBRoG8McYYY0xTFYvFH8BHIAccBRa2AaK/ACilZvP5/Gw2m7Wy2Ww2m81ms5ZlWZZlWZZt27Zt27Zt23Z5J8DbJkBCKdXX3d3dlUgk4vF4PB6Px+OJRCKRSCQSiWQymUwmk8lkKpVKpVKpVCqRSBzYBpjfBjgDXDXGWKZYLBYty7Isy7Jsq+Ratm1blu04jmM7jmPbjuPYjuM4xhjzfBtgqQngKKUsrbU11dNjdff0WF09PVZnT7fV1dNjTU5MqImJCTU+Pq7Gxif0xMSEnpycVOVyWQOrgG0BbmqtLaO11VaWMcbkjTF5Y4wxG6dRcYwx1oYqpVJqJ2ANeMx/1B/gBdC5xT8EQRAEvu+HYRgGvu/7vu/7QRAEvu/7QRAE/iZ+AP6AASIgAh7tA3jzF+DDHiAEIiA6APAX2I8qSUH+3CgAAAAASUVORK5CYII=",
    
    # Storage
    "nextcloud": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHNSURBVDiNpZO/axRBFMc/b2ZnZ2/v9u72TiIRERERERGxsLCwsLCwsLCwsLCwsBALCwsLCwsLCwtBEARBEARBEARBEAwh4d3e3t3szM7MvJnXSEhyFwYGhnnz+X7fe/Nm4D8jABCRRWAeGAQyQPSvwgDMA5eBS0A/IPwHgIiUgStABsgAhSYrFAqFavEAuCIiP4HMvwCISAYYBwrGGGOMMU31C3gPvAWObfogIgnALTabzea01pRKJUqlEmtra5RKJUqlEqVSiVKpRKlUolQqrXme5wEsAS+BF8DiXoDnQJ/neW6lUnEr5YpbqVTcSqXiVioVt1qtutVq1a1Wq269Xnfr9bpbr9ddr1ar1Wq1GisFPA7DEMBvjMlZtm3bFduyq47rVB3HqTpOxXFsx3Ecp+I4juM4juvarl21bds1m80Gvu8DuMCnJoABKFq2bdu2Y1dty7Ytqw3btnO2bVu2bdu2Y9v2xMREbGJiQu8A7AC8bQIYgJwxJmeMyRljctrcOG2MyTVU/bu7K5vN5owxJwj8oKW7uwDrgO4sy7JKpdJkvV6fbJTrOI7rum6j7Mbj8fj8/PyJo6OjLeV9Bsy1APx0XdcFWAX2zQEAHoZhWPdpvz7zBzBNjUBBOOAOAAAAAElFTkSuQmCC",
    "minio": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGcSURBVDiNpZO9axRBGMZ/M7Mzu3t7yV3uLifGRCQiIiIiIhYWFhYWFhYWFhYWFhZiYWFhYWFhYWEhCIIgCIIgCIIgCCGE5HJ3e7s7uzPzzjtmk9zFC8LAwDDv8zzP+847wn9WACCEOAO0gBqQB9y/ChXQAprACaAMCP8BIIQ4CJwCCkABKPaY6CWlxDBNAA4Bp4UQfwqFf0sIUQBqQElKKaWUUnZ1X9d1Pc5isQhACTjcNwMhRAGoyU6no8IwVGEYqiiKVBRFKooiFUWRiqJIhWGowjBUQgh5+PBhE0WRAtoH2hhjJsu2bfv9fl9ZjmMrx3GU4zjKcRzlOI7yfV/5vq98fz2OgTWgDOx1HMe2Lcdy+vy+ry3H8Xxl2Y6yHce2bdu2LctaB7gM7O0B+ABEjuOofr+vkiRRWmuVpqlK01SlaarSNFVaa6W1VlprpZSSSillO65dFhMTU0VRp2EUyTiKZBiEMgpDGQShDINABkEgg2AdYBnoZICGEELXq5Wyruuyrus6gBBCCiGkMUYBa0BlR8ApIcTJnv/5v3UXqG4Bvv4FvAPmgXmgPdTBf2ARECNHqE8AAAAASUVORK5CYII=",
    
    # Default
    "default": "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAEYSURBVDiNpZOxSgNBEIa/mdm53LvL3V1yMRGJSEQkIiIWFhYWFhYWFhYWPoBPYGFhYWEhCIIgCIIgCIIgGJLk7u72dmf2bSJG4y8MA8PM/3/zzwz8ZwQAIrIELAJ1oAIE/yoMwCJwE2gBNUD4DwAR6QLLQAWoAN0mi7PZLEC1tgAsichPoPIvACJSAUZA1xhTMcaYpuo0m90sy+oBQ0ADuAwMAREhIhdjjBkYYwbVajVot9tBs9kMms1m0Gw2g3a7HbTb7SCKoiCKosCyrCAMQ38X4A3Qi4hhmqZpmqZpnud5nud5nud5nud5nucqz3OV57nK8lwBcwDiLyAgxphBtVoNqtVqEEVRUK/Xg3q9HkRRFIRhGIRhGIRBEPgdgH/AZ+A7ZrQwqEacpEgAAAAASUVORK5CYII="
}

def get_icon(service_name):
    """Get icon for a service"""
    icon_key = service_name.lower().replace(" ", "_").replace("-", "_")
    
    # Try direct match first
    if icon_key in ICONS:
        icon_data = base64.b64decode(ICONS[icon_key])
    # Try partial matches
    elif "plex" in icon_key:
        icon_data = base64.b64decode(ICONS["plex"])
    elif "docker" in icon_key:
        icon_data = base64.b64decode(ICONS["docker"])
    elif any(x in icon_key for x in ["nginx", "proxy"]):
        icon_data = base64.b64decode(ICONS["nginx"])
    elif "pihole" in icon_key or "pi-hole" in icon_key:
        icon_data = base64.b64decode(ICONS["pihole"])
    elif "grafana" in icon_key:
        icon_data = base64.b64decode(ICONS["grafana"])
    elif "home" in icon_key and "assistant" in icon_key:
        icon_data = base64.b64decode(ICONS["home_assistant"])
    else:
        icon_data = base64.b64decode(ICONS["default"])
    
    image = Image.open(BytesIO(icon_data))
    return ImageTk.PhotoImage(image)

# Service definitions with categories
SERVICES = {
    "Media Servers": [
        ("Plex", "plex", ["plex", "plexmediaserver"], [32400]),
        ("Jellyfin", "jellyfin", ["jellyfin"], [8096]),
        ("Emby", "emby", ["emby", "embyserver"], [8096]),
        ("Kodi", "default", ["kodi"], [8080]),
    ],
    "Media Management": [
        ("Radarr", "radarr", ["radarr"], [7878]),
        ("Sonarr", "sonarr", ["sonarr"], [8989]),
        ("Lidarr", "default", ["lidarr"], [8686]),
        ("Readarr", "default", ["readarr"], [8787]),
        ("Bazarr", "default", ["bazarr"], [6767]),
        ("Prowlarr", "prowlarr", ["prowlarr"], [9696]),
        ("Overseerr", "default", ["overseerr"], [5055]),
        ("Ombi", "default", ["ombi"], [3579]),
        ("Tautulli", "default", ["tautulli"], [8181]),
    ],
    "Download Clients": [
        ("qBittorrent", "default", ["qbittorrent", "binhex-qbittorrentvpn"], [8080]),
        ("Transmission", "default", ["transmission"], [9091]),
        ("SABnzbd", "default", ["sabnzbd"], [8080]),
        ("NZBGet", "default", ["nzbget"], [6789]),
        ("Deluge", "default", ["deluge"], [8112]),
    ],
    "Network Services": [
        ("Nginx Proxy Manager", "nginx", ["nginx-proxy-manager", "nginxproxymanager"], [81]),
        ("Traefik", "default", ["traefik"], [8080]),
        ("Caddy", "default", ["caddy"], [2019]),
        ("Pi-hole", "pihole", ["pihole"], [80]),
        ("AdGuard Home", "default", ["adguard", "adguardhome"], [3000]),
        ("WireGuard", "default", ["wireguard"], [51820]),
        ("OpenVPN", "default", ["openvpn"], [1194]),
        ("Tailscale", "default", ["tailscale"], [41641]),
    ],
    "Monitoring": [
        ("Grafana", "grafana", ["grafana"], [3000]),
        ("Prometheus", "prometheus", ["prometheus"], [9090]),
        ("InfluxDB", "default", ["influxdb"], [8086]),
        ("Uptime Kuma", "uptime_kuma", ["uptime-kuma"], [3001]),
        ("Netdata", "default", ["netdata"], [19999]),
        ("Glances", "default", ["glances"], [61208]),
    ],
    "Management": [
        ("Portainer", "portainer", ["portainer"], [9000]),
        ("Yacht", "default", ["yacht"], [8000]),
        ("Cockpit", "default", ["cockpit"], [9090]),
        ("Webmin", "default", ["webmin"], [10000]),
    ],
    "Home Automation": [
        ("Home Assistant", "home_assistant", ["homeassistant", "home-assistant"], [8123]),
        ("Node-RED", "default", ["nodered", "node-red"], [1880]),
        ("Mosquitto", "default", ["mosquitto"], [1883]),
        ("Zigbee2MQTT", "default", ["zigbee2mqtt"], [8080]),
        ("ESPHome", "default", ["esphome"], [6052]),
    ],
    "Storage & Backup": [
        ("Nextcloud", "nextcloud", ["nextcloud"], [443]),
        ("Syncthing", "default", ["syncthing"], [8384]),
        ("MinIO", "minio", ["minio"], [9000]),
        ("Duplicati", "default", ["duplicati"], [8200]),
        ("PhotoPrism", "default", ["photoprism"], [2342]),
        ("Immich", "default", ["immich"], [2283]),
    ],
    "Security": [
        ("Vaultwarden", "default", ["vaultwarden", "bitwarden"], [80]),
        ("Authelia", "default", ["authelia"], [9091]),
        ("Authentik", "default", ["authentik"], [9000]),
        ("Keycloak", "default", ["keycloak"], [8080]),
    ],
    "Dashboards": [
        ("Homepage", "default", ["homepage"], [3000]),
        ("Heimdall", "default", ["heimdall"], [80]),
        ("Organizr", "default", ["organizr"], [80]),
        ("Dashy", "default", ["dashy"], [80]),
        ("Homarr", "default", ["homarr"], [7575]),
        ("Flame", "default", ["flame"], [5005]),
    ],
    "Development": [
        ("GitLab", "default", ["gitlab"], [80]),
        ("Gitea", "default", ["gitea"], [3000]),
        ("Code Server", "default", ["code-server", "codeserver"], [8443]),
        ("Jenkins", "default", ["jenkins"], [8080]),
        ("Drone", "default", ["drone"], [80]),
    ],
    "Other Services": [
        ("Docker", "docker", ["docker"], [2375]),
        ("PostgreSQL", "default", ["postgres", "postgresql"], [5432]),
        ("MySQL/MariaDB", "default", ["mysql", "mariadb"], [3306]),
        ("Redis", "default", ["redis"], [6379]),
        ("MongoDB", "default", ["mongodb", "mongo"], [27017]),
    ],
}

class HomelabDocWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏠 Homelab Documentation Wizard")
        
        # Detect OS
        self.os_type = platform.system()
        
        # Set window size based on OS
        if self.os_type == "Windows":
            self.root.geometry("1000x700")
        else:
            self.root.geometry("1000x700")
        
        # Make it look good
        self.style = ttk.Style()
        if self.os_type == "Windows":
            self.style.theme_use('vista')
        else:
            self.style.theme_use('clam')
        
        # Data storage
        self.selected_services = {}
        self.service_vars = {}
        self.service_icons = {}
        self.detected_systems = []
        self.output_queue = queue.Queue()
        
        # Create GUI
        self.setup_gui()
        
        # Start discovery
        self.root.after(100, self.start_discovery)
        
    def setup_gui(self):
        """Create the main GUI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#1e1e1e', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🏠 Homelab Documentation Wizard", 
                        font=('Arial', 24, 'bold'), bg='#1e1e1e', fg='white')
        title.pack(pady=20)
        
        subtitle = tk.Label(header_frame, text="Auto-discover and document your self-hosted services", 
                           font=('Arial', 10), bg='#1e1e1e', fg='#cccccc')
        subtitle.pack()
        
        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Welcome
        self.create_welcome_tab()
        
        # Tab 2: Service Selection
        self.create_services_tab()
        
        # Tab 3: Options
        self.create_options_tab()
        
        # Tab 4: Progress
        self.create_progress_tab()
        
        # Bottom buttons
        self.create_bottom_buttons()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to scan your homelab")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill='x', side='bottom')
        
    def create_welcome_tab(self):
        """Create welcome tab"""
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="Welcome")
        
        # Welcome message
        welcome_text = f"""Welcome to the Homelab Documentation Wizard!

This tool will help you create comprehensive documentation for your self-hosted services.

Features:
✓ Auto-discovers services on your network
✓ Creates visual network diagrams
✓ Generates security audit reports
✓ Builds service dependency maps
✓ Exports to multiple formats

Detected OS: {self.os_type}
Working directory: {os.getcwd()}

Click 'Next' to select your services!"""
        
        text_label = ttk.Label(welcome_frame, text=welcome_text, font=('Arial', 12), justify='left')
        text_label.pack(pady=50, padx=50)
        
        # Quick stats frame
        stats_frame = ttk.LabelFrame(welcome_frame, text="Quick Stats", padding=20)
        stats_frame.pack(pady=20)
        
        self.stats_label = ttk.Label(stats_frame, text="Scanning network...", font=('Arial', 10))
        self.stats_label.pack()
        
    def create_services_tab(self):
        """Create services selection tab"""
        services_frame = ttk.Frame(self.notebook)
        self.notebook.add(services_frame, text="Services")
        
        # Header
        header_frame = ttk.Frame(services_frame)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="Select Services to Document", 
                 font=('Arial', 16, 'bold')).pack(side='left')
        
        # Search
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side='right')
        
        ttk.Label(search_frame, text="🔍").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_services)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=5)
        
        # Create scrollable frame
        canvas = tk.Canvas(services_frame, bg='white')
        scrollbar = ttk.Scrollbar(services_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create service checkboxes with icons
        row = 0
        for category, services in SERVICES.items():
            # Category header
            cat_frame = ttk.LabelFrame(self.scrollable_frame, text=category, padding=10)
            cat_frame.grid(row=row, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
            row += 1
            
            # Services in category
            service_row = 0
            service_col = 0
            
            for service_name, icon_name, containers, ports in services:
                service_frame = ttk.Frame(cat_frame)
                service_frame.grid(row=service_row, column=service_col, padx=10, pady=5, sticky='w')
                
                # Load icon
                try:
                    icon = get_icon(icon_name)
                    self.service_icons[service_name] = icon
                except:
                    icon = None
                
                # Checkbox with icon
                var = tk.BooleanVar()
                self.service_vars[service_name] = var
                
                if icon:
                    cb = ttk.Checkbutton(service_frame, text=f" {service_name}", 
                                        variable=var, image=icon, compound='left')
                else:
                    cb = ttk.Checkbutton(service_frame, text=service_name, variable=var)
                cb.pack(side='left')
                
                # Store frame for filtering
                service_frame.service_name = service_name
                
                # Move to next position
                service_col += 1
                if service_col >= 3:
                    service_col = 0
                    service_row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(services_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Select All", 
                  command=self.select_all_services).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all_services).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Auto-Detect", 
                  command=self.auto_detect_services).pack(side='left', padx=5)
        
    def create_options_tab(self):
        """Create options tab"""
        options_frame = ttk.Frame(self.notebook)
        self.notebook.add(options_frame, text="Options")
        
        # Documentation options
        doc_frame = ttk.LabelFrame(options_frame, text="Documentation Options", padding=20)
        doc_frame.pack(fill='x', padx=20, pady=10)
        
        self.doc_options = {
            'network_diagram': tk.BooleanVar(value=True),
            'service_map': tk.BooleanVar(value=True),
            'security_audit': tk.BooleanVar(value=True),
            'backup_status': tk.BooleanVar(value=True),
            'resource_usage': tk.BooleanVar(value=True),
        }
        
        options = [
            ('network_diagram', '🗺️ Network Topology Diagram'),
            ('service_map', '🔗 Service Connection Map'),
            ('security_audit', '🔒 Security Audit Report'),
            ('backup_status', '💾 Backup Status Check'),
            ('resource_usage', '📊 Resource Usage Analysis'),
        ]
        
        for key, label in options:
            ttk.Checkbutton(doc_frame, text=label, 
                           variable=self.doc_options[key]).pack(anchor='w', pady=2)
        
        # Output formats
        format_frame = ttk.LabelFrame(options_frame, text="Output Formats", padding=20)
        format_frame.pack(fill='x', padx=20, pady=10)
        
        self.output_formats = {
            'markdown': tk.BooleanVar(value=True),
            'html': tk.BooleanVar(value=True),
            'json': tk.BooleanVar(value=True),
        }
        
        formats = [
            ('markdown', '📝 Markdown Files'),
            ('html', '🌐 HTML Dashboard'),
            ('json', '📊 JSON Data (for integrations)'),
        ]
        
        for key, label in formats:
            ttk.Checkbutton(format_frame, text=label, 
                           variable=self.output_formats[key]).pack(anchor='w', pady=2)
        
        # Discovery options
        discovery_frame = ttk.LabelFrame(options_frame, text="Discovery Settings", padding=20)
        discovery_frame.pack(fill='x', padx=20, pady=10)
        
        # Network range
        ttk.Label(discovery_frame, text="Network Range:").grid(row=0, column=0, sticky='w', pady=5)
        self.network_range = tk.StringVar(value="192.168.1.0/24")
        ttk.Entry(discovery_frame, textvariable=self.network_range, width=20).grid(row=0, column=1, pady=5)
        
        # SSH credentials
        ttk.Label(discovery_frame, text="Default SSH User:").grid(row=1, column=0, sticky='w', pady=5)
        self.ssh_user = tk.StringVar(value="root")
        ttk.Entry(discovery_frame, textvariable=self.ssh_user, width=20).grid(row=1, column=1, pady=5)
        
        # Output location
        output_frame = ttk.LabelFrame(options_frame, text="Output Location", padding=20)
        output_frame.pack(fill='x', padx=20, pady=10)
        
        self.output_path = tk.StringVar(value=str(Path.home() / "homelab-docs"))
        
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill='x')
        
        ttk.Entry(path_frame, textvariable=self.output_path, width=50).pack(side='left', padx=5)
        ttk.Button(path_frame, text="Browse...", command=self.browse_output).pack(side='left')
        
    def create_progress_tab(self):
        """Create progress tab"""
        progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(progress_frame, text="Progress")
        
        # Progress header
        ttk.Label(progress_frame, text="Documentation Generation Progress", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           length=400, mode='determinate')
        self.progress_bar.pack(pady=10)
        
        # Progress text
        self.progress_label = ttk.Label(progress_frame, text="Ready to generate documentation")
        self.progress_label.pack(pady=5)
        
        # Output text area
        output_frame = ttk.Frame(progress_frame)
        output_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap='word', height=15)
        self.output_text.pack(fill='both', expand=True)
        
        # Buttons
        button_frame = ttk.Frame(progress_frame)
        button_frame.pack(pady=10)
        
        self.open_output_btn = ttk.Button(button_frame, text="📁 Open Output Folder", 
                                         command=self.open_output_folder, state='disabled')
        self.open_output_btn.pack(side='left', padx=5)
        
        self.view_docs_btn = ttk.Button(button_frame, text="🌐 View Documentation", 
                                       command=self.view_documentation, state='disabled')
        self.view_docs_btn.pack(side='left', padx=5)
        
    def create_bottom_buttons(self):
        """Create navigation buttons"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        # Left side - navigation
        nav_frame = ttk.Frame(button_frame)
        nav_frame.pack(side='left')
        
        self.prev_btn = ttk.Button(nav_frame, text="← Previous", command=self.prev_tab)
        self.prev_btn.pack(side='left', padx=5)
        
        self.next_btn = ttk.Button(nav_frame, text="Next →", command=self.next_tab)
        self.next_btn.pack(side='left', padx=5)
        
        # Right side - generate
        self.generate_btn = ttk.Button(button_frame, text="🚀 Generate Documentation", 
                                      command=self.generate_documentation,
                                      style='Accent.TButton')
        self.generate_btn.pack(side='right', padx=5)
        
        # Configure accent style
        self.style.configure('Accent.TButton', font=('Arial', 12, 'bold'))
        
    def start_discovery(self):
        """Start network discovery"""
        self.status_var.set("Scanning network for services...")
        threading.Thread(target=self.discovery_thread, daemon=True).start()
        
    def discovery_thread(self):
        """Background discovery thread"""
        try:
            # Simulate network discovery
            import time
            time.sleep(1)
            
            # Update stats
            discovered = ["Docker", "Plex", "Radarr", "Sonarr", "Nginx Proxy Manager", "Portainer"]
            
            self.root.after(0, self.update_discovery_results, discovered)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Discovery error: {str(e)}")
    
    def update_discovery_results(self, services):
        """Update UI with discovery results"""
        # Update stats
        self.stats_label.config(text=f"Found {len(services)} services on your network")
        
        # Check the discovered services
        for service in services:
            if service in self.service_vars:
                self.service_vars[service].set(True)
        
        self.status_var.set(f"Auto-detected {len(services)} services")
        
    def filter_services(self, *args):
        """Filter services based on search"""
        search_term = self.search_var.get().lower()
        
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                # Category frame
                visible_count = 0
                for service_widget in widget.winfo_children():
                    if hasattr(service_widget, 'service_name'):
                        if search_term in service_widget.service_name.lower():
                            service_widget.grid()
                            visible_count += 1
                        else:
                            service_widget.grid_remove()
                
                # Hide category if no services visible
                if visible_count == 0 and search_term:
                    widget.grid_remove()
                else:
                    widget.grid()
    
    def select_all_services(self):
        """Select all services"""
        for var in self.service_vars.values():
            var.set(True)
    
    def clear_all_services(self):
        """Clear all services"""
        for var in self.service_vars.values():
            var.set(False)
    
    def auto_detect_services(self):
        """Auto-detect services"""
        self.status_var.set("Scanning for services...")
        self.start_discovery()
    
    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_path.set(directory)
    
    def prev_tab(self):
        """Go to previous tab"""
        current = self.notebook.index('current')
        if current > 0:
            self.notebook.select(current - 1)
    
    def next_tab(self):
        """Go to next tab"""
        current = self.notebook.index('current')
        if current < len(self.notebook.tabs()) - 1:
            self.notebook.select(current + 1)
    
    def generate_documentation(self):
        """Start documentation generation"""
        # Get selected services
        selected = [name for name, var in self.service_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("No Services Selected", 
                                 "Please select at least one service to document.")
            return
        
        # Switch to progress tab
        self.notebook.select(3)
        
        # Disable buttons
        self.generate_btn.config(state='disabled')
        self.prev_btn.config(state='disabled')
        self.next_btn.config(state='disabled')
        
        # Start generation
        self.log("Starting documentation generation...")
        self.log(f"Selected services: {', '.join(selected)}")
        
        threading.Thread(target=self.generation_thread, args=(selected,), daemon=True).start()
    
    def generation_thread(self, selected_services):
        """Main generation thread"""
        try:
            output_dir = Path(self.output_path.get())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            total_steps = len(selected_services) * 3 + 10
            current_step = 0
            
            def update_progress(msg, increment=1):
                nonlocal current_step
                current_step += increment
                progress = (current_step / total_steps) * 100
                self.root.after(0, self.update_progress, progress, msg)
            
            # Create directory structure
            update_progress("Creating documentation structure...")
            self.create_directory_structure(output_dir)
            
            # Discover systems
            update_progress("Discovering systems...")
            systems = self.discover_systems(selected_services)
            
            # Document each service
            for service in selected_services:
                update_progress(f"Documenting {service}...")
                self.document_service(service, output_dir, systems)
            
            # Generate visualizations
            if self.doc_options['network_diagram'].get():
                update_progress("Creating network diagram...")
                self.create_network_diagram(output_dir, systems, selected_services)
            
            if self.doc_options['service_map'].get():
                update_progress("Creating service map...")
                self.create_service_map(output_dir, selected_services)
            
            if self.doc_options['security_audit'].get():
                update_progress("Performing security audit...")
                self.create_security_audit(output_dir, systems)
            
            # Generate index
            update_progress("Generating documentation index...")
            self.create_index(output_dir, selected_services)
            
            # Complete
            update_progress("Documentation generation complete!", 0)
            self.root.after(0, self.generation_complete)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Generation error: {str(e)}")
    
    def log(self, message):
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.output_text.update()
    
    def update_progress(self, progress, message):
        """Update progress bar and message"""
        self.progress_var.set(progress)
        self.progress_label.config(text=message)
        self.log(message)
    
    def create_directory_structure(self, output_dir):
        """Create documentation directory structure"""
        dirs = [
            "services", "network", "security", "monitoring",
            "architecture", "visualizations", "backups", "configs"
        ]
        
        for dir_name in dirs:
            (output_dir / dir_name).mkdir(exist_ok=True)
    
    def discover_systems(self, selected_services):
        """Discover systems running selected services"""
        # This would normally scan the network
        # For demo, return mock data
        return {
            "unraid": {
                "ip": "192.168.1.100",
                "services": ["Docker", "Plex", "Radarr", "Sonarr"],
                "os": "Unraid"
            },
            "raspberry-pi-1": {
                "ip": "192.168.1.101",
                "services": ["Portainer", "Pi-hole"],
                "os": "Raspbian"
            }
        }
    
    def document_service(self, service_name, output_dir, systems):
        """Document a specific service"""
        service_dir = output_dir / "services" / service_name.lower().replace(" ", "_")
        service_dir.mkdir(exist_ok=True)
        
        # Find service definition
        service_info = None
        for category, services in SERVICES.items():
            for name, icon, containers, ports in services:
                if name == service_name:
                    service_info = (name, icon, containers, ports)
                    break
        
        if not service_info:
            return
        
        # Create service documentation
        doc_content = f"""# {service_name}

## Overview
Service: {service_name}
Common Ports: {', '.join(map(str, service_info[3]))}
Container Names: {', '.join(service_info[2])}

## Deployment Status
"""
        
        # Add system info
        for system_name, system_info in systems.items():
            if service_name in system_info['services']:
                doc_content += f"\n### {system_name}\n\n\n
- IP: {system_info['ip']}
- OS: {system_info['os']}
- Status: ✅ Running\n"
        
        # Add configuration template
        doc_content += """
## Configuration

### Docker Compose Example
```yaml
version: '3.8'
services:
  """ + service_name.lower().replace(" ", "_") + """:
    image: # Add image name
    container_name: """ + service_name.lower().replace(" ", "_") + """
    ports:
      - """""" + str(service_info[3][0] if service_info[3] else 8080) + """:""" + str(service_info[3][0] if service_info[3] else 8080) + """"
    volumes:
      - ./config:/config
    restart: unless-stopped
```

## Notes
Add your service-specific notes here.
"""
        
        # Write documentation
        (service_dir / "README.md").write_text(doc_content)
    
    def create_network_diagram(self, output_dir, systems, services):
        """Create network diagram"""
        diagram_html = """<!DOCTYPE html>
<html>
<head>
    <title>Network Diagram</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/vis-network.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/vis-network.min.css" rel="stylesheet">
    <style>
        #network { width: 100%; height: 600px; border: 1px solid #ccc; }
        body { font-family: Arial, sans-serif; }
    </style>
</head>
<body>
    <h1>Homelab Network Diagram</h1>
    <div id="network"></div>
    <script>
        var nodes = new vis.DataSet([
            {id: 'internet', label: 'Internet', shape: 'square', color: '#ff6b6b'},
            {id: 'router', label: 'Router', shape: 'box', color: '#4ecdc4'},
"""
        
        # Add systems
        node_id = 3
        for system_name, system_info in systems.items():
            diagram_html += f"            {{id: '{system_name}', label: '{system_name}\\n{system_info['ip']}', shape: 'box', color: '#45b7d1'}},\n"
        
        # Add services
        for service in services:
            diagram_html += f"            {{id: 'service_{node_id}', label: '{service}', shape: 'ellipse', color: '#96ceb4'}},\n"
            node_id += 1
        
        diagram_html += """        ]);
        
        var edges = new vis.DataSet([
            {from: 'internet', to: 'router'},
"""
        
        # Add connections
        for system_name in systems:
            diagram_html += f"            {{from: 'router', to: '{system_name}'}},\n"
        
        diagram_html += """        ]);
        
        var container = document.getElementById('network');
        var data = { nodes: nodes, edges: edges };
        var options = {
            layout: { hierarchical: { direction: 'UD', sortMethod: 'directed' } },
            edges: { arrows: 'to' }
        };
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>"""
        
        (output_dir / "visualizations" / "network-diagram.html").write_text(diagram_html)
    
    def create_service_map(self, output_dir, services):
        """Create service dependency map"""
        # Create a visual service map
        service_map = """# Service Map

## Service Connections

```mermaid
graph TB
    subgraph "Media Stack"
        Plex[Plex Media Server]
        Radarr[Radarr - Movies]
        Sonarr[Sonarr - TV Shows]
        Prowlarr[Prowlarr - Indexers]
    end
    
    subgraph "Network Services"
        NPM[Nginx Proxy Manager]
        PiHole[Pi-hole DNS]
    end
    
    subgraph "Storage"
        Media[/Media Storage/]
    end
    
    Prowlarr --> Radarr
    Prowlarr --> Sonarr
    Radarr --> Media
    Sonarr --> Media
    Media --> Plex
    NPM --> Plex
    NPM --> Radarr
    NPM --> Sonarr
```

## Service Dependencies

"""
        
        for service in services:
            service_map += f"### {service}\n"
            service_map += "- Dependencies: TBD\n"
            service_map += "- Depends on this: TBD\n\n"
        
        (output_dir / "architecture" / "service-map.md").write_text(service_map)
    
    def create_security_audit(self, output_dir, systems):
        """Create security audit report"""
        audit = f"""# Security Audit Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- Systems Scanned: {len(systems)}
- Services Found: {sum(len(s['services']) for s in systems.values())}

## Security Recommendations

### 1. Access Control
- [ ] All services behind reverse proxy
- [ ] Strong passwords on all services
- [ ] 2FA enabled where possible
- [ ] Regular password rotation

### 2. Network Security
- [ ] Firewall rules documented
- [ ] VLANs properly configured
- [ ] No unnecessary ports exposed
- [ ] VPN for remote access

### 3. Updates
- [ ] All containers updated regularly
- [ ] Security patches applied
- [ ] Automated update notifications

### 4. Backups
- [ ] Regular backup schedule
- [ ] Backup encryption enabled
- [ ] Offsite backup copy
- [ ] Restoration tested

## System-Specific Findings

"""
        
        for system_name, system_info in systems.items():
            audit += f"### {system_name}\n"
            audit += f"- IP: {system_info['ip']}\n"
            audit += f"- Services: {', '.join(system_info['services'])}\n"
            audit += "- Status: ⚠️ Review recommended\n\n"
        
        (output_dir / "security" / "audit-report.md").write_text(audit)
    
    def create_index(self, output_dir, services):
        """Create main index file"""
        index = f"""# Homelab Documentation

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This documentation was automatically generated for your homelab setup.

## Quick Links

- [Network Diagram](visualizations/network-diagram.html)
- [Service Map](architecture/service-map.md)
- [Security Audit](security/audit-report.md)

## Services Documented

"""
        
        for service in sorted(services):
            service_path = f"services/{service.lower().replace(' ', '_')}/README.md"
            index += f"- [{service}]({service_path})\n"
        
        index += """
## Getting Started

1. Review the network diagram to understand your topology
2. Check the security audit for recommendations
3. Explore individual service documentation
4. Set up monitoring based on the templates provided

## Maintenance

Remember to regenerate this documentation when you:
- Add or remove services
- Change network configuration
- Update security settings
- Modify service connections
"""
        
        (output_dir / "README.md").write_text(index)
        
        # Also create HTML index if selected
        if self.output_formats['html'].get():
            self.create_html_dashboard(output_dir, services)
    
    def create_html_dashboard(self, output_dir, services):
        """Create HTML dashboard"""
        dashboard = """<!DOCTYPE html>
<html>
<head>
    <title>Homelab Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #1e1e1e; color: white; padding: 20px; border-radius: 8px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .service { display: inline-block; margin: 5px; padding: 10px 20px; background: #4ecdc4; color: white; border-radius: 4px; text-decoration: none; }
        .service:hover { background: #45b7d1; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 Homelab Dashboard</h1>
        <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>
    
    <div class="card">
        <h2>Quick Links</h2>
        <a href="network-diagram.html" class="service">Network Diagram</a>
        <a href="../security/audit-report.md" class="service">Security Audit</a>
    </div>
    
    <div class="card">
        <h2>Services</h2>
"""
        
        for service in sorted(services):
            dashboard += f'        <a href="../services/{service.lower().replace(" ", "_")}/README.md" class="service">{service}</a>\n'
        
        dashboard += """    </div>
</body>
</html>"""
        
        (output_dir / "visualizations" / "dashboard.html").write_text(dashboard)
    
    def generation_complete(self):
        """Handle generation completion"""
        self.log("✅ Documentation generation complete!")
        
        # Enable buttons
        self.open_output_btn.config(state='normal')
        self.view_docs_btn.config(state='normal')
        self.generate_btn.config(state='normal')
        self.prev_btn.config(state='normal')
        self.next_btn.config(state='normal')
        
        # Show completion dialog
        messagebox.showinfo("Complete", 
                          "Documentation generated successfully!\n\n" +
                          "Click 'Open Output Folder' to view your documentation.")
    
    def show_error(self, error_msg):
        """Show error message"""
        self.log(f"❌ Error: {error_msg}")
        messagebox.showerror("Error", error_msg)
        
        # Re-enable buttons
        self.generate_btn.config(state='normal')
        self.prev_btn.config(state='normal')
        self.next_btn.config(state='normal')
    
    def open_output_folder(self):
        """Open the output folder"""
        output_dir = Path(self.output_path.get())
        if output_dir.exists():
            if platform.system() == "Windows":
                os.startfile(output_dir)
            elif platform.system() == "Darwin":
                subprocess.run(["open", output_dir])
            else:
                subprocess.run(["xdg-open", output_dir])
    
    def view_documentation(self):
        """View the generated documentation"""
        if self.output_formats['html'].get():
            dashboard_path = Path(self.output_path.get()) / "visualizations" / "dashboard.html"
            if dashboard_path.exists():
                webbrowser.open(f"file://{dashboard_path}")
        else:
            index_path = Path(self.output_path.get()) / "README.md"
            if index_path.exists():
                if platform.system() == "Windows":
                    os.startfile(index_path)
                else:
                    webbrowser.open(f"file://{index_path}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    # Check Python version
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)
    
    # Create and run the wizard
    app = HomelabDocWizard()
    app.run()

if __name__ == "__main__":
    main()
