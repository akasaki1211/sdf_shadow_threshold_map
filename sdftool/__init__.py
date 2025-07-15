import os
from typing import List, Literal, Optional
import numpy as np
import cv2
import logging

VERSION = '0.3.2'

logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(levelname)s] %(asctime)s | %(message)s'
)

def load_image_with_grayscale(image_path:str, binarization:bool=False) -> np.ndarray:
    """
    Args:
        image_path (str): 8bit grayscale image path
        binarization (bool, optional): Binarize. Defaults to False.

    Returns:
        np.ndarray: 8-bit grayscale image
    """

    img = cv2.imread(image_path)
    if img is None:
        logging.warning("Image '{}' could not be loaded.".format(image_path))
        return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    
    if binarization:
        _, gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY) 

    logging.info("Image '{}' is loaded.".format(image_path))
    
    return gray

def save_image(
        img_normalized:np.ndarray, 
        output_path:str, 
        bit_depth:Literal[8, 16]=8, 
        color_mode:Literal['gray', 'rgb', 'rgba']='gray',
        alpha_normalized:Optional[np.ndarray]=None,
        confirm_overwrite: bool = False
    ) -> None:

    """
    Args:
        img_normalized (np.ndarray): Image normalized to 0.0 ~ 1.0
        output_path (str): Output PNG Path
        bit_depth (int, optional): Output PNG bit depth (8 or 16). Defaults to 8.
        color_mode (Literal['gray', 'rgb', 'rgba'], optional): The color mode of the output image ('gray', 'rgb', and 'rgba'). Defaults to 'gray'.
        alpha_normalized (np.ndarray, optional): Alpha image normalized to 0.0 ~ 1.0. Used only when color_mode is set to 'rgba'.
    """
    
    if not bit_depth in [8, 16]:
        bit_depth = 8

    if color_mode == 'rgba' and alpha_normalized is None:
        color_mode == 'rgb'
    
    scale_factor = 255 if bit_depth == 8 else 65535
    dtype = np.uint8 if bit_depth == 8 else np.uint16

    # convert dtype
    img_dtype_conversion = (img_normalized * scale_factor).astype(dtype)
    
    # color mode
    if color_mode == 'gray':
        img = img_dtype_conversion
    elif color_mode == 'rgb':
        img = cv2.merge([img_dtype_conversion, img_dtype_conversion, img_dtype_conversion])
    else:
        alpha_dtype_conversion = (alpha_normalized * scale_factor).astype(dtype)
        img = cv2.merge([img_dtype_conversion, img_dtype_conversion, img_dtype_conversion, alpha_dtype_conversion])

    # save
    if confirm_overwrite and os.path.exists(output_path):
        response = input(f"File '{output_path}' already exists. Overwrite? [y/n]: ").strip().lower()
        if response not in ('y', 'yes'):
            logging.info(f"Skipped saving to '{output_path}' (overwrite not confirmed).")
            return

    cv2.imwrite(output_path, img)
    logging.info("Saved to '{}'".format(output_path))

def img_lerp(start:float, end:float, factor:np.ndarray) -> np.ndarray:
    return start + (end - start) * factor

def get_image_difference(img1:np.ndarray, img2:np.ndarray) -> np.ndarray:
    img1_norm = cv2.normalize(img1, None, 0, 1.0, cv2.NORM_MINMAX)
    img2_norm = cv2.normalize(img2, None, 0, 1.0, cv2.NORM_MINMAX)
    return np.abs(img2_norm.astype(np.float64) - img1_norm.astype(np.float64))

def generate_sdf(img_binary:np.ndarray, distanceType=cv2.DIST_L2, maskSize=cv2.DIST_MASK_PRECISE) -> np.ndarray:
    """
    Args:
        img_binary (np.ndarray): 8-bit grayscale image binarized (0 or 255)
        distanceType (int, optional): Distance type. Defaults to cv2.DIST_L2.
        maskSize (int, optional): Mask size, 0 or 3 or 5. Defaults to cv2.DIST_MASK_PRECISE (=0).

    Returns:
        np.ndarray: Normalized (0.0 ~ 1.0) SDF image
    """
    
    dist_inside = cv2.distanceTransform(img_binary, distanceType, maskSize)
    dist_outside = cv2.distanceTransform((255 - img_binary), distanceType, maskSize)
    
    sdf = dist_outside - dist_inside
    sdf = np.abs(sdf)

    sdf_normalized = cv2.normalize(sdf, None, 0, 1.0, cv2.NORM_MINMAX)
    
    return sdf_normalized.astype(np.float64)

def create_gradient_from_sdf(sdf1_normalized:np.ndarray, sdf2_normalized:np.ndarray) -> np.ndarray:

    denominator = sdf1_normalized + sdf2_normalized
    denominator = np.where(denominator == 0, 1, denominator) # 0除算対策

    gradient = sdf1_normalized / denominator
    gradient_normalized = cv2.normalize(gradient, None, 0, 1.0, cv2.NORM_MINMAX)

    return gradient_normalized


def generate_shadow_threshold_map(
        image_paths:List[str], 
        output_path:str,
        bit_depth:Literal[8, 16]=8, 
        color_mode:Literal['gray', 'rgb', 'rgba']='gray',
        reverse:bool=False, 
        save_temp:bool=False,
        filter_mode:Literal['none', 'gaussian', 'bilateral']='none',
        gaussian_kernel:int=3,
        bilateral_d:int=3
    ) -> None:

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if save_temp:
        temp_dir = os.path.join(os.path.dirname(output_path), 'temp')
        os.makedirs(temp_dir, exist_ok=True)

    image_paths.sort()

    # load images with grayscale
    grayscale_images = []
    for path in image_paths:
        image = load_image_with_grayscale(path, binarization=True)
        if image is not None:
            grayscale_images.append(image)
    image_count = len(grayscale_images)
    logging.info("{} images loaded.".format(image_count))

    # step values
    gradient_count = image_count - 1
    interval = 1.0 / gradient_count
    step_values = [(interval * i, interval * (i + 1)) for i in range(gradient_count)]

    # generate sdf
    sdf_images = [generate_sdf(img) for img in grayscale_images]
    
    if save_temp:
        for i, sdf in enumerate(sdf_images):
            temp_path = os.path.join(temp_dir, 'step_1_sdf_{}.png'.format(str(i+1).zfill(2)))
            save_image(sdf, temp_path, bit_depth=bit_depth)

    gradient_maps = []
    mask_maps = []
    
    for i in range(gradient_count):
        img1, img2 = grayscale_images[i], grayscale_images[i+1]
        sdf1, sdf2 = sdf_images[i], sdf_images[i+1]
        s, e = step_values[i]

        if reverse:
            s = 1 - s
            e = 1 - e
        
        logging.info('Processing images: {}, {} (step: {:.5f} - {:.5f})'.format(os.path.basename(image_paths[i]), os.path.basename(image_paths[i+1]), s, e))

        # generate mask
        mask = get_image_difference(img1, img2)
        mask_maps.append(mask)

        # generate gradient
        gradient = create_gradient_from_sdf(sdf1, sdf2)

        # lerp and mask
        masked_gradient = img_lerp(s, e, gradient) * mask

        if save_temp:
            idx = str(i+1).zfill(2)
            temp_path = os.path.join(temp_dir, 'step_2_mask_{}.png'.format(idx))
            save_image(mask, temp_path, bit_depth=bit_depth)
            temp_path = os.path.join(temp_dir, 'step_3_combine_sdf_{}.png'.format(idx))
            save_image(gradient, temp_path, bit_depth=bit_depth)
            temp_path = os.path.join(temp_dir, 'step_4_lerp_and_mask_{}.png'.format(idx))
            save_image(masked_gradient, temp_path, bit_depth=bit_depth)

        gradient_maps.append(masked_gradient)

    # result
    shadow_threshold_map = np.sum(gradient_maps, axis=0)

    # filter
    if filter_mode == 'gaussian':
        shadow_threshold_map = cv2.GaussianBlur(shadow_threshold_map, (gaussian_kernel, gaussian_kernel), 0)
    elif filter_mode == 'bilateral':
        shadow_threshold_map = cv2.bilateralFilter(shadow_threshold_map.astype(np.float32), bilateral_d, 75, 75)
    
    merged_mask = None
    if color_mode == 'rgba':
        merged_mask = np.sum(mask_maps, axis=0)
    
    # save
    save_image(
        shadow_threshold_map, 
        output_path, 
        bit_depth=bit_depth, 
        color_mode=color_mode, 
        alpha_normalized=merged_mask,
        confirm_overwrite=True
    )