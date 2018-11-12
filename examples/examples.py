from flaschenQ7client.flaschenQ7client import FlaschenQ7Client
import time
from PIL import Image

FLaImg = FlaschenQ7Client('localhost', 1337, display_width=256, display_height=96, multi_threading=True, protocol="UDP")
FLaImg.clear_all()

im1 = Image.new('RGB', (16, 16), color='red')
FLaImg.send(im1, y_offset=80, x_vel=8, y_vel=-8, timeout=10, y_gravity=1, x_max=256-16,
            y_max=96-16, layer=1, action_at_limit="inverse_single")

im2 = Image.new('RGB', (8, 8), color='blue')
FLaImg.send(im2, y_offset=80, x_offset=250, x_vel=-8, y_vel=-8, timeout=10, layer=2,
            y_gravity=1, y_max=96-8, action_at_limit="stop_all")

im3 = Image.new('RGB', (8, 8), color='orange')
FLaImg.send(im3, y_offset=40, x_offset=40, x_vel=-8, y_vel=-8, timeout=10,
            y_gravity=1, layer=3, x_min=0, x_max=256-8, y_min=0, y_max=96-8, action_at_limit="stop_single")

im4 = Image.new('RGB', (16, 16), color='green')
FLaImg.send(im4, y_offset=30, x_vel=8, y_vel=-4, timeout=10, y_min=0, x_min=0, x_max=256-16,
            y_max=96-16, layer=4, action_at_limit="inverse_single")

im5 = Image.new('RGB', (16, 16), color='yellow')
FLaImg.send(im5, y_offset=48, x_acc=4, timeout=10, x_min=0, x_max=256-16,
            layer=5, action_at_limit="reset_vel_inverse_all")

while FLaImg.is_running():
    time.sleep(.1)
