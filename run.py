import os
import argparse

import sdftool

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputdir", type=str, default='input', help='Input directory path')
    parser.add_argument("-o", "--outputdir", type=str, default='output', help='Output directory path')
    parser.add_argument("-n", "--outputname", type=str, default='shadow_threshold_map', help='Output file name')
    parser.add_argument("-b", "--bitdepth", type=int, choices=[8, 16], default=8, help='Output PNG bit depth (8 or 16)')
    parser.add_argument("-r", "--reverse", type=bool, default=False, help='Reverse the gradient direction')
    parser.add_argument("-t", "--savetemp", type=bool, default=False, help='Save the image during processing')
    return parser.parse_args()

if __name__ == "__main__":

    opt = parse_arguments()

    # load input files
    filelist = []
    for f in os.listdir(opt.inputdir):
        path = os.path.join(opt.inputdir, f)
        if os.path.isfile(path):
            filelist.append(path)
    
    # set output path
    output_path = os.path.join(os.path.abspath(opt.outputdir), opt.outputname + '.png')
    
    # run
    sdftool.generate_shadow_threshold_map(
        filelist, 
        output_path,
        bit_depth=opt.bitdepth,
        reverse=opt.reverse, 
        save_temp=opt.savetemp
    )