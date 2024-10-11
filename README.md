[日本語README](README_jp.md)  

Create a **Shadow Threshold Map** by interpolating SDF (Signed Distance Field).  

![top.png](.images/top.png)

The algorithm is based on the following link:  
🔗[SDF Based Transition Blending for Shadow Threshold Map - ながむしメモ](https://nagakagachi.hatenablog.com/entry/2024/03/02/140704)  

> **Tested with**
> - Windows 11
> - Python 3.10.9
> - numpy 2.0.0
> - opencv-python 4.10.0.84

## Getting Started
If you use the exe from [Releases](https://github.com/akasaki1211/sdf_shadow_threshold_map/releases), you do not need this step. For more details, see [here](#using-exe).
```
python -m venv venv
venv\scripts\activate
pip install numpy opencv-python
```

**Basic :**  
Specify a directory containing only image files with the `-i` option. The images in the directory will be processed in ascending order.  
```powershell
python run.py -i 'sample/sample1'
```

**with Options :**  
You can also run it with some additional options.  
```powershell
python run.py -i 'sample/sample2' -o 'output2' -n 'face_map' -b 16 -c "rgb" -r -t
```

## Options
- `-i`, `--inputdir` : Specify the input directory path where contains only images. This is a required option.
- `-o`, `--outputdir` : Specify the output directory path where images will be saved. Default is 'output'.
- `-n`, `--outputname` : Specify the base name for the output PNG file. Default is 'shadow_threshold_map'.
- `-b`, `--bitdepth` : Set the bit depth for output PNG files. Valid options are 8 or 16. Default is 8.
- `-c`, `--colormode`, Select the color mode for the output images. Options are 'gray', 'rgb', or 'rgba'. Default is 'gray'.
- `-r`, `--reverse` : Enable to reverse the gradient direction.
- `-t`, `--savetemp` : Enable to save intermediate images during the processing.
- `-f`, `--filtermode` : Select the filter mode for the image processing. Choices are 'none' (no filtering), 'gaussian' (apply Gaussian blur), or 'bilateral' (apply bilateral filter). Default is 'none'.
- `-k`, `--kernel_size` : Kernel size for Gaussian Blur. It must be an odd number. Default is 3.
- `-d`, `--diameter` : Diameter of the pixel neighborhood for Bilateral Filter. Default is 3.

### `--bitdepth`
16-bit images have smoother shadow boundaries than 8-bit images. However, be aware that the file size and load will be higher.

![bitdepth.png](.images/bitdepth.png)

### `--colormode`
If the color mode is set to 'rgb', the grayscale image will be duplicated in three channels. If the color mode is set to 'rgba', the transition region is added to the alpha channel.

![colormode.png](.images/colormode.png)

### `--reverse`
Reverses the gradient direction.

![reverse.png](.images/reverse.png)

### `--savetemp`
Saves the intermediate images created during processing in `outputdir\temp`. This is for debugging purposes.  

- step 1 : SDF image obtained from the input image
- step 2 : Mask created from the pair of input images
- step 3 : Gradient obtained from the pair of SDF images
- step 4 : Lerp with the gradient and masked image

![savetemp.png](.images/savetemp.png)

### `--filtermode`
A blur filter can be applied to the generated image. The available options are **Gaussian Blur** and **Bilateral Filter**. Gaussian should be used with `--kernel_size`, and bilateral with `--diameter`. The larger the value, the stronger the blur.  

```powershell
python run.py -i "sample/sample1" -f "gaussian" -k 5
python run.py -i "sample/sample1" -f "bilateral" -d 5
```

![filtermode.png](.images/filtermode.png)

## Using exe
If you do not have Python installed, use the exe. Download from [Releases](https://github.com/akasaki1211/sdf_shadow_threshold_map/releases).

```powershell
ShadowThresholdMap.exe -i 'sample/sample1'
```

```powershell
ShadowThresholdMap.exe -i 'sample/sample2' -o 'output2' -n 'face_map' -b 16 -c "rgb" -r -t
```

### bat

The [`gen.bat`](bat/gen.bat) in the [`bat`](bat) folder makes the above command easier to use.  
Place `ShadowThresholdMap.exe` downloaded from [Releases](https://github.com/akasaki1211/sdf_shadow_threshold_map/releases) in the `bat` folder, and drag and drop the folder containing the source images onto `gen.bat`.

![use_bat](.images/use_bat.png)

`gen.bat` contains the minimum command arguments. Please change the options as appropriate.

```batchfile
@echo off

if "%~1"=="" exit

:: show version
echo Using version:
%~dp0ShadowThresholdMap.exe -v

:: run
%~dp0ShadowThresholdMap.exe -i %~1

::(example) add options
::%~dp0ShadowThresholdMap.exe -i %~1 -b 16 -r -n "face_shadow_map" -c "rgba" -f "gaussian" -k 3
```

## Reference Links
- [SDF Based Transition Blending for Shadow Threshold Map - ながむしメモ](https://nagakagachi.hatenablog.com/entry/2024/03/02/140704)
- [UE5 SDF Face Shadowマッピングでアニメ顔用の影を作ろう - Let's Enjoy Unreal Engine](https://unrealengine.hatenablog.com/entry/2024/02/28/222220)
- [Get \*PERFECT\* Anime Face Shadows (Easier Way) in Blender - YouTube](https://www.youtube.com/watch?v=x-K6bCAl6Qs)
- [GDC Vault - 3D Toon Rendering in 'Hi-Fi RUSH'](https://gdcvault.com/play/1034330/3D-Toon-Rendering-in-Hi)