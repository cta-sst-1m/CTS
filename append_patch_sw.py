import sys
from cts_core import camera

digicam = camera.Camera('config/camera_config_old.cfg')
fnew = open(sys.argv[1],'r')
f = open('config/camera_config_old.cfg','r')
fout = open(sys.argv[2],'w')

for line in f.readlines():
    # Skip lines with comments
    if '#' in line:
        fout.write(line)
        continue
    # Get the old pixel number and replace it with new one
    new_line = line.split('\n')[0].split('\t')
    pixel_id = int(new_line[6])
    new_line+=[str(digicam.Pixels[pixel_id].patch)]
    str_new_line = ''
    opt= '\t'
    for i,st in enumerate(new_line):
        if i == len(new_line)-1:
            opt = '\n'
        str_new_line+=st+opt
    fout.write(str_new_line)
f.close()
fout.close()
