
def load_events(filename = "/home/sterody/Documents/codes_pour_la_camera/gamma_0.csv",n_evt_in_file=100):
    
    input_file = open(filename,"r")
    
    dict_pix = {}
    
    for i in range(n_evt_in_file):
        dict_pix[i]={}
        index[i]={}
        line_str = input_file.readline()
        line_list = line_str.split(' CRLF\n')[0].split(',')
    
        for j in range(1296):
            dict_pix[i][j]=int(line_list[j+6])
                   
    input_file.close()
    return dict_pix
    
        

def load_event(evtnum, filename = "/home/sterody/Documents/codes_pour_la_camera/gamma_0.csv",n_evt_in_file=100):
    '''
    Description de la fonction:Elle permet de prendre en entree le fichier gamma,
    le nombre de lignes dans le fichier gamma_0,le numero de ligne sur lequel on veut faire le traitement et ressort
    le dictionnaire de pixel
    Input : 
    
    Output: 
    
    '''
    
    ## Ouverture du fichier
    input_file = open(filename,"r")
    
    for i in range(n_evt_in_file):
        dict_pix={}
        ## lit la ligne suivante
        line_str = input_file.readline()
        ## si l'evenement ne correspond pas a l'evenement demande passe a l'evenenemebt suivant
        if i!=evtnum:
            continue
        
        line_list = line_str.split(' CRLF\n')[0].split(',')
    
        for j in range(1296):
            dict_pix[j]=int(line_list[j+6])
            
            
        input_file.close()
        return dict_pix
    

def compute_led_patches_mean(cts,result,calib = 2.):
    ## Which are the camera patches matching the LED patches
    camera_patches = cts.patch_camera_to_patch_led
    camera_pixels = cts.pixel_to_led['AC']
    
    camera_patches_mean,pixels_status = {},{}

    ## Loop over the camera patches    
    for cam_patch in camera_patches.keys():
        ## Get the list of pixel ID in this patch (id: cam_patch)
        patch_pixelIDs = cts.camera.Patches[cam_patch].pixelsID 
        camera_patches_mean[cam_patch]=0.
        ## Loop over the pixel id to compute the mean
        for pixelID in patch_pixelIDs:
            camera_patches_mean[cam_patch]+=float(result[pixelID])/3.*calib
        for pixelID in patch_pixelIDs:
            if camera_patches_mean[cam_patch]!=0:   
                pixels_status[pixelID]=True
            else:
                pixels_status[pixelID]=False
                        
                    #for pixelID in patch_pixelIDs:
                    #    leds_status[camera_pixels[pixelID]]=pixels_status[pixelID]
                    
                    ## Get the mean by led patch ID
                    #led_patch = camera_patches[cam_patch]
                    #led_patches_mean[led_patch]=camera_patches_mean[cam_patch]
                    
    return camera_patches_mean,pixels_status




