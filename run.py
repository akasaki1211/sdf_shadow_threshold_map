import os
import argparse

import sdftool

def parse_arguments():
    parser = argparse.ArgumentParser(description="Create a Shadow Threshold Map by interpolating SDF (Signed Distance Field).")
    parser.add_argument('-v', '--version', action='version', version=sdftool.VERSION)
    parser.add_argument("-i", "--inputdir", type=str, required=True, help="Specify the input directory path where contains only images. This is a required option.")
    parser.add_argument("-o", "--outputdir", type=str, default='output', help="Specify the output directory path where images will be saved. Default is 'output'.")
    parser.add_argument("-n", "--outputname", type=str, default='shadow_threshold_map', help="Specify the base name for the output PNG file. Default is 'shadow_threshold_map'.")
    parser.add_argument("-b", "--bitdepth", type=int, choices=[8, 16], default=8, help="Set the bit depth for output PNG files. Valid options are 8 or 16. Default is 8.")
    parser.add_argument("-c", "--colormode", type=str, choices=['gray', 'rgb', 'rgba'], default='gray', help="Select the color mode for the output images. Options are 'gray', 'rgb', or 'rgba'. Default is 'gray'.")
    parser.add_argument("-r", "--reverse", action='store_true', help="Enable to reverse the gradient direction.")
    parser.add_argument("-t", "--savetemp", action='store_true', help="Enable to save intermediate images during the processing.")
    parser.add_argument("-f", "--filtermode", type=str, choices=['none', 'gaussian', 'bilateral'], default='none', help="Select the filter mode for the image processing. Choices are 'none' (no filtering), 'gaussian' (apply Gaussian blur), or 'bilateral' (apply bilateral filter). Default is 'none'.")
    parser.add_argument("-k", "--kernel_size", type=int, default=3, help="Kernel size for Gaussian Blur. It must be an odd number. Default is 3.")
    parser.add_argument("-d", "--diameter", type=int, default=3, help="Diameter of the pixel neighborhood for Bilateral Filter. Default is 3.")
    return parser.parse_args()

def get_file_list(directory):
    filelist = []
    for f in sorted(os.listdir(directory)):
        path = os.path.join(directory, f)
        if os.path.isfile(path):
            filelist.append(path)
    return filelist

def main():
    opt = parse_arguments()

    # load input files
    try:
        filelist = get_file_list(opt.inputdir)
    except FileNotFoundError:
        print("Error: {} does not exist.".format(opt.inputdir))
        return
    
    # set output path
    output_path = os.path.join(os.path.abspath(opt.outputdir), opt.outputname + '.png')
    
    # run
    sdftool.generate_shadow_threshold_map(
        filelist, 
        output_path,
        bit_depth=opt.bitdepth,
        color_mode=opt.colormode,
        reverse=opt.reverse, 
        save_temp=opt.savetemp,
        filter_mode=opt.filtermode,
        gaussian_kernel=opt.kernel_size,
        bilateral_d=opt.diameter
    )

if __name__ == "__main__":
    main()