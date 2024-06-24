Create a **Shadow Threshold Map** by interpolating SDF (Signed Distance Field).

> **Tested with**
> - Windows 10
> - Python 3.10.9
> - numpy 2.0.0
> - opencv-python 4.10.0.84

## Getting Started
```
python -m venv venv
venv\scripts\activate
pip install numpy opencv-python
```

**Basic :**
```powershell
python run.py -i 'sample/sample1'
```

**with Options :**
```powershell
python run.py -i 'sample/sample2' -o 'output2' -n 'face_map' -b 16 -r true -t true
```

## Options
- `-i`, `--inputdir` (str) : Input directory path. Default is 'input'.
- `-o`, `--outputdir` (str) : Output directory path. Default is 'output'.
- `-n`, `--outputname` (str) : Output file name. Default is 'shadow_threshold_map'.
- `-b`, `--bitdepth` (int) : Output PNG bit depth (8 or 16). Default is 8.
- `-r`, `--reverse` (bool) : Reverse the gradient direction. Default is false.
- `-t`, `--savetemp` (bool) : Save the image du ring processing. Default is false.