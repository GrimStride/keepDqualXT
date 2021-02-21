import sys, curses, os, imghdr
from wand.image import Image
from datetime import datetime

def init():
    print('keepDqualXT v1.0 by Grim Stride\n')
    getpath()

def getpath():
    while True:
        OgTex = input('Enter original texture filepath or type \"exit()\" to exit the application\n')
        if OgTex == 'exit()': sys.exit()
        elif os.path.isfile(OgTex):
            with open(OgTex, 'rb+') as f:
                f.seek(0x0054)
                check = f.read(4)
                if check == b'DXT5':
                    f.seek(0x000C)
                    ogw = int.from_bytes(f.read(4), "little")
                    ogh = int.from_bytes(f.read(4), "little")
                    break
                else: print('Error: not a DXT5 texture file\n')
        else: print('Error: file not found\n')
    while True:
        ModTex = input('\nEnter modified texture filepath or type \"exit()\" to exit the application\n')
        if ModTex == 'exit()': sys.exit()
        elif ModTex == OgTex: print('Error: texture is the same')
        elif os.path.isfile(ModTex):
            with open(ModTex, 'rb+') as f:
                f.seek(0x0054)
                check = f.read(4)
                if check == b'DXT5':
                    f.seek(0x000C)
                    mdw = int.from_bytes(f.read(4), "little")
                    mdh = int.from_bytes(f.read(4), "little")
                    if mdw == ogw and mdh == ogh: break
                    else: print('Error: modified texture dimensions do not match original texture dimensions')
                else: print('Error: not a DXT5 texture file')
        else: print('Error: file not found')
    option = input('\nDo you want to supply a diff texture (Y/N)? (Must be equal or 1/4 the size of the supplied textures)\n')
    while True:
        if not option.upper() in ['Y', 'N', 'YES', 'NO']: print('Error: invalid option')
        else: break
        option = input()
    if option.upper() in ['Y', 'YES']:
        while True:
            DiffTex = input('\nEnter diff texture filepath\n')
            if DiffTex == OgTex or DiffTex == ModTex: print('Error: texture is the same')
            elif os.path.isfile(DiffTex):
                isimg= imghdr.what(DiffTex)
                if isimg != None:
                    with Image(filename=DiffTex) as dif:
                        difw, difh = dif.size
                        if (difw == ogw and difh == ogh) or (difw == ogw/4 and difh == ogh/4): break
                        else: print('Error: diff texture size is not equal or 1/4 the size of the supplied textures')
                else: print('Error: file is not a recognized image format')
            else: print('Error: file not found')
    else:
        gendiff(OgTex, ModTex)
    process(OgTex, ModTex, DiffTex)

def gendiff(original, modified):
    i = 1
    with Image(filename=original) as og:
        with Image(filename=modified) as mod:
            og.fuzz = og.quantum_range * 0.02
            result = og.compare(mod, highlight="White", lowlight="Black")
            with result:
                if os.path.isfile('diff.png'):
                    while True:
                        test = 'diff' + str(i) + '.png'
                        if not os.path.isfile(test):
                            result.save(filename=test)
                            DiffTex = test
                            break
                        else: i += 1
                else:
                    result.save(filename='diff.png')
                    DiffTex = 'diff.png'
    return DiffTex
    

def process(original, modified, diff):
    with Image(filename=original) as s:
        ogw, ogh = s.size
    with Image(filename=diff) as img:
        wi = 0
        hi = 0
        width, height = img.size
        with open(original, 'rb+') as og:
            data = bytearray(og.read(128))
            with open(modified, 'rb+') as mod:
                og.seek(0x00000080)
                mod.seek(0x00000080)
                if width == ogw/4 and height == ogh/4:
                    while True:
                        dxtquad = str(img[wi,hi])
                        if dxtquad == "srgb(255,255,255)":
                            data += mod.read(16)
                            og.seek(16, 1)
                        else:
                            data += og.read(16)
                            mod.seek(16, 1)
                        if wi == width-1:
                            hi += 1
                            wi = 0
                            print("row" + str(hi))
                        else: wi += 1
                        if hi == height:
                            with open('result ' + datetime.now().strftime('%d-%m-%Y %H-%M-%S'), "wb") as output:
                                output.write(data)
                            print("Done!!!")
                            break
                elif width == ogw and height == ogh:
                    while True:
                        dxtquad = [str(img[wi,hi]), str(img[wi+1,hi]), str(img[wi+2,hi]), str(img[wi+3,hi]), str(img[wi,hi+1]), str(img[wi+1,hi+1]), str(img[wi+2,hi+1]), str(img[wi+3,hi+1]), str(img[wi,hi+2]), str(img[wi+1,hi+2]), str(img[wi+2,hi+2]), str(img[wi+3,hi+2]), str(img[wi,hi+3]), str(img[wi+1,hi+3]), str(img[wi+2,hi+3]), str(img[wi+3,hi+3])]                        
                        if "srgb(255,255,255)" in dxtquad:
                            data += mod.read(16)
                            og.seek(16, 1)
                        else:
                            data += og.read(16)
                            mod.seek(16, 1)
                        if wi == ogw-1:
                            hi += 4
                            wi = 0
                            print("row" + str(hi))
                        else: wi += 1
                        if hi == ogh:
                            with open('result ' + datetime.now().strftime('%d-%m-%Y %H-%M-%S'), "wb") as output:
                                output.write(data)
                            print("Done!!!")
                            break
                else: print('Error: diff texture size is not equal or 1/4 the size of the supplied textures')
    if n in globals(): getpath()

if __name__ == "__main__":
    global n
    n = 0
    init()
