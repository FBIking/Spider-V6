import socket
import struct
import time
from PIL import ImageGrab
import io

def main():
    # --- IMPORTANT ---
    # Change this to the IP address of the machine running server.py
    HOST = '127.0.0.1'
    # -----------------
    
    PORT = 9999

    print(f"Attempting to connect to {HOST}:{PORT}")
    
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                print(f"Connected to {HOST}:{PORT}")
                while True:
                    # Grab the screen using Pillow
                    img = ImageGrab.grab()

                    # Save to a memory buffer as JPEG
                    mem_file = io.BytesIO()
                    # Convert to RGB to ensure compatibility with JPEG format
                    img_rgb = img.convert('RGB')
                    img_rgb.save(mem_file, 'jpeg', quality=75) # Sending as JPEG
                    mem_file.seek(0)
                    frame = mem_file.read()

                    # Pack the frame size and send it, followed by the frame data
                    s.sendall(struct.pack(">L", len(frame)) + frame)
                    
                    time.sleep(0.1) # control frame rate
        except ConnectionRefusedError:
            print("Connection refused. Server not running? Retrying in 5 seconds...")
            time.sleep(5)
        except (ConnectionResetError, BrokenPipeError):
            print("Connection lost. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    main()
