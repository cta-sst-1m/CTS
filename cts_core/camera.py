import sys
import numpy as np

if sys.version_info[0] == 3:
    import cts_core.geometry as gp
else:
    import geometry as gp

fadc_dict = {31: [30, 0, 0, 30, 7, "L", 1, 2], 33: [32, 0, 0, 32, 8, "L", 2, 0],
             34: [33, 0, 0, 33, 8, "L", 2, 1], 27: [26, 0, 1, 26, 6, "L", 0, 2],
             28: [27, 0, 1, 27, 6, "L", 0, 3], 32: [31, 0, 1, 31, 7, "L", 1, 3],
             7: [6, 1, 2, 17, 4, "R", 4, 1], 9: [8, 1, 2, 15, 3, "R", 3, 3],
             10: [9, 1, 2, 14, 3, "R", 3, 2], 3: [2, 1, 3, 20, 5, "R", 5, 0],
             4: [3, 1, 3, 22, 5, "R", 5, 2], 8: [7, 1, 3, 16, 4, "R", 4, 0],
             29: [28, 0, 4, 28, 7, "L", 1, 0], 35: [34, 0, 4, 34, 8, "L", 2, 2],
             36: [35, 0, 4, 35, 8, "L", 2, 3], 25: [24, 0, 5, 24, 6, "L", 0, 0],
             26: [25, 0, 5, 25, 6, "L", 0, 1], 30: [29, 0, 5, 29, 7, "L", 1, 1],
             5: [4, 1, 6, 19, 4, "R", 4, 3], 11: [10, 1, 6, 13, 3, "R", 3, 1],
             12: [11, 1, 6, 12, 3, "R", 3, 0], 1: [0, 1, 7, 23, 5, "R", 5, 3],
             2: [1, 1, 7, 21, 5, "R", 5, 1], 6: [5, 1, 7, 18, 4, "R", 4, 2],
             43: [42, 2, 8, 42, 10, "L", 4, 2], 45: [44, 2, 8, 44, 11, "L", 5, 0],
             46: [45, 2, 8, 46, 11, "L", 5, 2], 39: [38, 2, 9, 38, 9, "L", 3, 2],
             40: [39, 2, 9, 39, 9, "L", 3, 3], 44: [43, 2, 9, 43, 10, "L", 4, 3],
             19: [18, 3, 10, 5, 1, "R", 1, 1], 21: [20, 3, 10, 3, 0, "R", 0, 3],
             22: [21, 3, 10, 2, 0, "R", 0, 2], 15: [14, 3, 11, 9, 2, "R", 2, 1],
             16: [15, 3, 11, 8, 2, "R", 2, 0], 20: [19, 3, 11, 4, 1, "R", 1, 0],
             41: [40, 2, 12, 40, 10, "L", 4, 0], 47: [46, 2, 12, 45, 11, "L", 5, 1],
             48: [47, 2, 12, 47, 11, "L", 5, 3], 37: [36, 2, 13, 36, 9, "L", 3, 0],
             38: [37, 2, 13, 37, 9, "L", 3, 1], 42: [41, 2, 13, 41, 10, "L", 4, 1],
             17: [16, 3, 14, 7, 1, "R", 1, 3], 23: [22, 3, 14, 1, 0, "R", 0, 1],
             24: [23, 3, 14, 0, 0, "R", 0, 0], 13: [12, 3, 15, 11, 2, "R", 2, 3],
             14: [13, 3, 15, 10, 2, "R", 2, 2], 18: [17, 3, 15, 6, 1, "R", 1, 2]}


class Pixel:
    """
    Base class for pixel representation

    """

    def __init__(
            self,
            _x,
            _y,
            _id,
            _id_in_module,
            _id_in_patch,
            _module,
            _fadc,
            _fadc_quad,
            _fadc_chan,
            _sector,
            _patch,
            _canNode,
            _canMaster):
        # Pixel Center
        """

        :type _fadc: object
        :type _id_in_patch: Pixel identifier in patch
        """
        self.center = (_x, _y)
        # Pixel ID (software ID)
        self.ID = _id
        # Pixel ID in its module
        self.id_inModule = _id_in_module
        # Pixel ID in its patch
        self.id_inPatch = _id_in_patch
        # Pixel ID in its FADC board
        self.id_inFADC = _fadc_chan
        # Pixel ID in its crate
        self.in_inCrate = (_fadc - 1) * 48 + _fadc_chan - 1
        # Module ID
        self.module = _module
        # CAN node ID
        self.CANnode = _canNode
        # CAN master ID
        self.CANmaster = _canMaster
        # FADC ID
        self.fadc = _fadc
        # FADC Quad ID
        self.fadcQuad = _fadc_quad
        # FADC Channel ID
        self.fadcChannel = _fadc_chan
        # Sector ID
        self.sector = _sector
        # Patch ID
        self.patch = _patch
        # FADC Internal mapping: channel in rj45
        self.id_inFADC_rj45_channel = fadc_dict[self.id_inFADC][0]
        # FADC Internal mapping: module number
        self.id_inFADC_module = fadc_dict[self.id_inFADC][1]
        # FADC Internal mapping: patch number
        self.id_inFADC_patch = fadc_dict[self.id_inFADC][2]
        self.fadcInternalChannel = fadc_dict[self.id_inFADC][3]
        self.fadcInternalQuad = fadc_dict[self.id_inFADC][4]
        # FADC Internal mapping: quad column
        self.fadcQuad_column = fadc_dict[self.id_inFADC][5]
        self.fadcQuad_number = fadc_dict[self.id_inFADC][6]
        self.fadcQuad_channel = fadc_dict[self.id_inFADC][7]

        # Initialise the rotation to apply to the pixel graphic representation
        rotation = 0.
        if self.sector == 2:
            rotation = 240.
        elif self.sector == 1:
            rotation = 120.
        # Create the list of vertices for each pixels
        self.Vertices = gp.createPixel(_x, _y, d=24.3, rotation=rotation)
        # Create TGraph out of it


class Patch():
    """
    Base class for patch representation

    """

    def __init__(self, _id):
        # Patch ID (software)
        self.ID = _id
        # Module ID
        self.module = -1
        # FADC ID
        self.fadc = -1
        # Sector ID
        self.sector = -1
        # List of Pixel id in patch
        self.pixelsID = []
        # List of ids of pixel in module in patch
        self.pixelsID_inModule = []
        # List of pixels
        self.pixels = [None] * 3

    def initialise(self):
        """
        Initialise function to be called once the pixel list have been filled
        """
        for p in self.pixels:
            self.pixelsID_inModule.append(p.id_inModule)
            self.pixelsID.append(p.ID)
        if set(self.pixelsID_inModule) == {1, 2, 5}:
            self.pixelsID_inModule = [1, 2, 5]
            self.id_inModule = 1
        elif set(self.pixelsID_inModule) == {3, 4, 7}:
            self.pixelsID_inModule = [3, 4, 7]
            self.id_inModule = 2
        elif set(self.pixelsID_inModule) == {6, 10, 9}:
            self.pixelsID_inModule = [6, 10, 9]
            self.id_inModule = 3
        elif set(self.pixelsID_inModule) == {8, 12, 11}:
            self.pixelsID_inModule = [8, 12, 11]
            self.id_inModule = 4

        self.module = self.pixels[0].module
        self.fadc = self.pixels[0].fadc
        self.sector = self.pixels[0].sector
        # Get the proper order of pixels vertices
        _vertices = []
        for pixid in self.pixelsID_inModule:
            for p in self.pixels:
                if p.id_inModule != pixid:
                    continue
                _vertices.append(p.Vertices)
        # Create the list of vertices representing the patch
        self.Vertices = gp.createPatch(_vertices)

    def appendPixel(self, idx, pix):
        """
        A function to append the pixels to the patch
        """
        self.pixels[idx] = pix

class Cluster_7():
    """
    Base class for Cluster of 7 patches representation
    """

    def __init__(self, _id):

        self.ID = _id
        self.patchesID = []
        self.pixelsID = []
        self.patches = []
        self.pixels = []


    def initialize(self):

        """
        Initialise function to be called once the patches list have been filled
        """

        for index, pat in enumerate(self.patches):

            for pix in self.patches[index].pixels:

                self.pixels.append(pix)


    def appendPatch(self, pat_id, pat):

        self.patches.append(pat)
        self.patchesID.append(pat_id)

    def appendPixel(self, pix_id, pix):

        self.pixels.append(pix)
        self.pixelsID.append(pix_id)




#class Cluster_19():




class Module():
    """
    Base class for module representation

    """

    def __init__(self, _id):
        # Module ID
        self.ID = _id
        # FADC ID
        self.fadc = -1
        # Sector ID
        self.sector = -1
        # List of pixel ID belonging to the module
        self.pixelsID = []
        # List of ID in module of the pixels belonging to the module
        self.pixelsID_inModule = []
        # List of pixels
        self.pixels = [None] * 12
        # List of patches ID belonging to the module
        self.patchesID = []
        # List of ID in module of the patches belonging to the module
        self.patchesID_inModule = []
        # List of patches
        self.patches = [None] * 4

    def initialise(self):
        """
        Initialise function to be called once the pixel and patches list have been filled
        """
        if len(self.pixels) == 0 or None in self.pixels:
            print('Pixels have not been initiated')
        if len(self.patches) == 0 or None in self.patches:
            print('Patches have not been initiated')
        for p in self.pixels:
            self.pixelsID_inModule.append(p.id_inModule)
            self.pixelsID.append(p.ID)
            self.pixelsID.append(p.ID)
        for p in self.patches:
            self.patchesID_inModule.append(p.id_inModule)
            self.patchesID.append(p.ID)

        self.sector = self.pixels[0].sector
        self.id_inSector = (self.ID - 1) % 36 + 1
        self.fullID = self.ID - 1 + 36 * (self.sector - 1)
        self.fadc = self.pixels[0].fadc

        self.Vertices = gp.createModule([p.Vertices for p in self.pixels])

    def appendPixel(self, idx, pix):
        """
        A function to append the pixels to the module
        """
        self.pixels[idx - 1] = pix

    def appendPatch(self, idx, pat):
        """
        A function to append the patches to the module
        """
        self.patches[idx - 1] = pat


class Camera():
    """
    Base class for the camera representation

    """

    def __init__(self, _config_file, _config_file_cluster=None):

        # Get the configuration from file
        f = open(_config_file, 'r')
        keys = []
        line = ''
        while '# HEADER' not in line:
            line = f.readline()
        keys = f.readline().split('# ')[1].split('\n')[0].split('\t')
        line = f.readline()
        lines = list(
            map(list, zip(*[l.split('\n')[0].split('\t') for l in f.readlines()])))
        _map_dict = dict(zip(keys, lines))
        for k in _map_dict.keys():
            if k.count('[mm]') > 0:
                _map_dict[k] = [float(x) for x in _map_dict[k]]
            elif k.count('column') > 0:
                _map_dict[k] = [str(x) for x in _map_dict[k]]
            else:
                _map_dict[k] = [int(x) for x in _map_dict[k]]

        # Sort by pixel
        for k in filter(lambda x: x != 'pixel_sw', _map_dict.keys()):
            _map_dict[k] = [v[1]
                            for v in sorted(zip(_map_dict['pixel_sw'], _map_dict[k]))]
        # _map_dict['pixel_sw'].sort()

        # Create the pixelList
        self.Pixels = [
            Pixel(
                _map_dict['x[mm]'][i],
                _map_dict['y[mm]'][i],
                p,
                _map_dict['pixel_in_module'][i],
                _map_dict['pixel_in_patch'][i],
                _map_dict['module'][i],
                _map_dict['fadc_board_in_mcr'][i],
                _map_dict['fadc_quad_in_fadc_board'][i],
                _map_dict['pixel_in_fadc_board'][i],
                _map_dict['can_master'][i],
                _map_dict['patch_sw'][i],
                _map_dict['can_node'][i],
                _map_dict['can_master'][i]) for i,
                                                p in enumerate(
                _map_dict['pixel_sw'])]
        # Create patches
        self.Patches = [Patch(i) for i in range(max(_map_dict['patch_sw']) + 1)]
        # Create modules
        self.Modules = [Module(i)
                        for i in range(1, max(_map_dict['module']) + 1)]
        # Create clusters

        if _config_file_cluster is not None:

            clusters_dict = np.load(_config_file_cluster)
            patches_in_cluster = clusters_dict['patches_in_cluster']
            self.Clusters_7 = [Cluster_7(id) for id in range(len(patches_in_cluster))] #TODO chaeck numbering

        # Append the pixels to patches and modules and initialisiation functions
        for p in self.Pixels:
            self.Patches[p.patch].appendPixel(p.id_inPatch, p)
            self.Modules[p.module - 1].appendPixel(p.id_inModule, p)

        for p in self.Patches:
            p.initialise()
        for p in self.Patches:
            self.Modules[p.module - 1].appendPatch(p.id_inModule, p)
        for i, p in enumerate(self.Modules):
            p.initialise()

        if _config_file_cluster is not None:

            for index, clust_id in enumerate(range(len(self.Clusters_7))):
                for pat_id in patches_in_cluster[index]:

                    self.Clusters_7[clust_id].appendPatch(pat_id, self.Patches[pat_id])

                self.Clusters_7[clust_id].appendPatch(self.Clusters_7[clust_id].ID, self.Patches[self.Clusters_7[clust_id].ID])

        self.list_config = [
            'can_master',
            'can_node',
            'module',
            'micro_crate',
            'fadc_board_in_mcr',
            'pixel_in_module',
            'pixel_sw',
            'fadc_quad_in_fadc_board',
            'pixel_in_fadc_board',
            'x[mm]',
            'y[mm]',
            'sector',
            'pixel_in_module_sw',
            'pixel_in_patch',
            'patch_sw',
            'pixel_in_fadc_board_rj45',
            'module_in_fadc_board',
            'patch_in_fadc_board',
            'fadc_quad_column_in_fadc_board',
            'fadc_quad_number_in_fadc_board',
            'fadc_quad_channel_in_fadc_board',
            'fadc_channel_internal_in_fadc_board',
            'fadc_quad_internal_in_fadc_board'
        ]

        self.dict_config = {
            'can_master': 'CANmaster',
            'can_node': 'CANnode',
            'module': 'module',
            'micro_crate': 'CANmaster',
            'fadc_board_in_mcr': 'fadc',
            'pixel_in_module': 'id_inModule',
            'pixel_sw': 'ID',
            'pixel_in_fadc_board': 'fadcChannel',
            'fadc_quad_in_fadc_board': 'fadcQuad',
            'x[mm]': 'center',
            'y[mm]': 'center',
            'sector': 'sector',
            'pixel_in_module_sw': 'id_inModule',
            'pixel_in_patch': 'id_inPatch',
            'patch_sw': 'patch',
            'pixel_in_fadc_board_rj45': 'id_inFADC_rj45_channel',
            'module_in_fadc_board': 'id_inFADC_module',
            'patch_in_fadc_board': 'id_inFADC_patch',
            'fadc_quad_column_in_fadc_board': 'fadcQuad_column',
            'fadc_quad_number_in_fadc_board': 'fadcQuad_number',
            'fadc_quad_channel_in_fadc_board': 'fadcQuad_channel',
            'fadc_channel_internal_in_fadc_board': 'fadcInternalChannel',
            'fadc_quad_internal_in_fadc_board': 'fadcInternalQuad'
        }

        self.dict_description = {
            'can_master': 'CAN master (old Can_master)',
            'can_node': 'CAN node (old Can_node)',
            'module': 'Module ID (old Module)',
            'micro_crate': 'Micro crate ID (old MCR)',
            'fadc_board_in_mcr': 'FADC board ID (old FADC_Board)',
            'pixel_in_module': 'Pixel ID in module [1-12], (old Pixel_number)',
            'pixel_sw': 'Software ID of the pixel (old PixelID)',
            'pixel_in_fadc_board': 'Pixel ID in FADC board (old FADC_Chan)',
            'fadc_quad_in_fadc_board': 'FADC Quadrant (old FADC_Quad)',
            'x[mm]': 'Abscisse of the pixel center',
            'y[mm]': 'Ordinate of the pixel center',
            'sector': 'Sector ID',
            'pixel_in_module_sw': 'Pixel ID in the module [0-11]',
            'pixel_in_patch': 'Pixel ID in the patch',
            'patch_sw': 'Patch ID in software',
            'pixel_in_fadc_board_rj45': 'Pixel ID in FADC board (for RJ45)',
            'module_in_fadc_board': 'Module ID in FADC Board',
            'patch_in_fadc_board': 'Patch ID in FADC board',
            'fadc_quad_column_in_fadc_board': 'FADC Quad column',
            'fadc_quad_number_in_fadc_board': 'FADC Quad number',
            'fadc_quad_channel_in_fadc_board': 'FADC Quad channel',
            'fadc_channel_internal_in_fadc_board': 'FADC Internal Channel number',
            'fadc_quad_internal_in_fadc_board': 'FADC Internal Quadrant number'
        }

    def generate_configfile(self, conf_file_name):
        # Can_master    Can_node        Module  MCR     FADC_Board      Pixel_number    PixelID FADC_Quad       FADC_Chan       x[mm]   y[mm]


        f = open(conf_file_name, 'w')
        f.write('#### Configuration file describing the mapping of SST-1M at hardware and software level\n')
        for conf in self.list_config:
            line = '# ' + conf + ' : ' + self.dict_description[conf]
            f.write(line + '\n')
        f.write('#\n')
        f.write('# HEADER\n')
        line, opt = '# ', ''
        for conf in self.list_config:
            line += opt + conf
            opt = '\t'
        line += '\n# DATA\n'
        f.write(line)
        for p in self.Pixels:
            line, opt = '', ''
            for conf in self.list_config:
                if conf not in ['x[mm]', 'y[mm]', 'fadc_quad_column_in_fadc_board']:
                    val = getattr(p, self.dict_config[conf])
                    if conf == 'pixel_sw_in_module':
                        val -= 1
                    line += opt + str(int(val))
                elif conf == 'fadc_quad_column_in_fadc_board':
                    line += opt + getattr(p, self.dict_config[conf])
                else:
                    line += opt + str(float((getattr(p, self.dict_config[conf])[0] if conf == 'x[mm]' else
                                             getattr(p, self.dict_config[conf])[1])))
                opt = '\t'
            f.write(line + '\n')
        f.close()


if __name__ == '__main__':
    c = Camera('../data/camera_config.cfg')
    c.generate_configfile('configuration_new.txt')
