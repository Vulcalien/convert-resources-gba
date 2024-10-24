# Copyright 2024 Vulcalien
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PIL import Image

def build_palette(bpp: int, filepath: str, mappings: list[str]):
    color_count = 2 ** bpp
    result = {}

    # read palette file
    if filepath is not None:
        img = Image.open(filepath).convert('RGB')
        for y in range(img.height):
            for x in range(img.width):
                pix = img.getpixel( (x, y) )

                if pix not in result:
                    result[pix] = (x + y * img.width) % color_count

    # parse mappings
    if mappings is not None:
        for mapping in mappings:
            color_str, index_str = mapping.split('=')

            color = string_to_rgb(color_str)
            index = int(index_str) % color_count

            result[color] = index

    return result

def string_to_rgb(arg: str):
    arg = arg.lstrip('#')
    return tuple(int(arg[i:i+2], 16) for i in (0, 2, 4))

class DataWriter:

    output = None

    datatype = None
    datasize = None
    typedef  = None

    threshold   = None
    write_count = 0

    def __init__(self, output_file, datatype: str):
        self.output = output_file

        DATATYPES = {
            'u8':  { 'size': 1, 'typedef': 'unsigned char'  },
            'u16': { 'size': 2, 'typedef': 'unsigned short' }
        }

        self.datatype = datatype
        if datatype in DATATYPES:
            self.datasize = DATATYPES[datatype]['size']
            self.typedef  = DATATYPES[datatype]['typedef']
        else:
            raise ValueError('unknown data type: ' + datatype)

        # set newline threshold
        self.threshold = 8

    def begin(self, name: str, static: bool, size: int):
        f = self.output

        f.write('typedef ' + self.typedef + ' ' + self.datatype + ';\n')

        if static:
            f.write('static ')
        f.write('const ' + self.datatype + ' ' + name)
        f.write('[' + str(size) + ']')
        f.write(' = {\n')

    def write(self, value: int):
        f = self.output

        # write value as an hexadecimal string
        f.write(f'0x%0{2 * self.datasize}x,' % value)

        # if necessary, add a newline
        if self.write_count % self.threshold == self.threshold - 1:
            f.write('\n')
        self.write_count += 1

    def end(self):
        f = self.output

        # if necessary, add a missing newline
        if self.write_count % self.threshold != 0 :
            f.write('\n')

        f.write('};\n')
