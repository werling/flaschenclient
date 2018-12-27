from flaschenclient.flaschenclient import FlaschenClient
import time
from PIL import Image

FlaTaClient = FlaschenClient('localhost', 1337, display_width=256, display_height=96)
FlaTaClient.clear_all()

im = Image.open("earth.gif")

FlaTaClient.send(im, width=64, height=64, timeout=10, layer=2, x_offset=128-32, y_offset=48-32,
                 action_at_limit="inverse_all", zoom_vel=2, width_max=128, width_min=8)

while FlaTaClient.is_running():
    time.sleep(.1)


