
import qrcode
import shortuuid
from PIL import ImageDraw, ImageFont

class CreateQR:
    '''Handles functions for creating unique file name and QR code'''

    @staticmethod
    def generate_uuid(username):
        '''generates the unique qr code'''
        uuid = shortuuid.ShortUUID().random(length=4)
        user_qr = username + "-" + uuid
        
        img = qrcode.make(user_qr) # generate unique code with img
        edit_img = ImageDraw.Draw(img)
        myFont = ImageFont.truetype('arial.ttf', 21) # pick font and size you want to add
        #myFont = ImageFont.truetype('/home/lukasgraig/.local/share/fonts/arial.ttf', 21) # this is the correct code to run on server

        x = CreateQR.__calc_text_coords(myFont, img, user_qr)
        edit_img.text((x, 8), user_qr, font=myFont, stroke_fill=15) # add the text to the image // x @ 94, y @ 295 is best but calc is still WIP
        #img.show()

        save_img = user_qr + '.png' # add png to the file
        img.save(f'..\storganizesite\storganize\static\qr_photo\{save_img}', 'PNG') # save the img
        #img.save(f'/home/lukasgraig/storaganizesite/storganize/static/qr_photo/{save_img}', 'PNG') # save the img to the server

        return uuid

    def __calc_text_coords(font, img, user_qr):
        '''calculates the middle of the image to put the text of the user code
        returns new coordinates for the text for the image '''
        tup = img.size # gets x, y coords for img size in pixels
        text_length = font.getlength(user_qr) # gets the font length in pixels
        calculated_x = (tup[0] - text_length) / 1.8 # x coordinate calculation for text x coord
        #print(f"{calculated_x} for {user_qr}")
        return calculated_x