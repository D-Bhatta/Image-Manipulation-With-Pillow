import os
import image_manipulation

im = image_manipulation.Pillow()

class TestObject(object):
    def test_testing(self):
        assert 1 == 1, "Testing failed"

    def check_data(self):
        data = im.pillow_image_data()
        assert data == [('Size:(width, height): ', (512, 512)), ('Format: ', 'PNG'), ('Mode: ', 'RGB'), ('Max and min values of RGB: ', ((54, 255), (3, 248), (8, 225))), ('Pixel data at (0,0) : ', (226, 137, 125))], "Error loading image"
    