# PointCloudSystem

<!-- https://medium.com/@samunyi90/how-to-make-custom-language-badges-for-your-profile-using-shields-io-ec69ea95dfc0 -->
[![](https://img.shields.io/badge/Windows-10-0078D6?style=flat-square&logo=Windows)](https://www.microsoft.com/en-us/windows/)
[![](https://img.shields.io/badge/Cuda-10.2-6B8E23?style=flat-square&logo=Nvidia)](https://pytorch.org/)
[![](https://img.shields.io/badge/Python-3.8-3776AB?style=flat-square&logo=Python)](https://www.python.org/)
[![](https://img.shields.io/badge/PyTorch-000000?style=flat-square&logo=PyTorch)](https://pytorch.org/)

## System
🤔 Installing OpenPCDet (and generally all other 3D object detection repositories) on a Windows device can be extremely tedious, as most of the open-source dependencies for OpenPCDet are not well-maintained on Windows. Therefore, we explicitly define our device system as follows for your reference:
1. Operating System (OS): Windows 10
2. CUDA version: 10.2
3. Python version: 3.8
4. PyTorch version: 1.10.1

So far, we have been able to reimplement this repository as long as the following system conditions are met. Ensure you are using Windows 10 and CUDA 10.2. We will guide you through setting up the remaining Python dependencies in the next section.

## Setup
⚠️ Please follow the sequence! Any other sequence may result in unknown errors which no one has solved before.

Conda environment
```bash
conda create --name windowspointcloud python=3.8 -y
conda activate windowspointcloud

git clone https://github.com/WindowsPointCloud/PointCloudSystem.git
cd PointCloudSystem
```

Install pytorch and spconv. Find the installation command via [pytorch get started](https://pytorch.org/get-started/previous-versions/) and [spconv repo](https://github.com/traveller59/spconv)
```
# Install torch version 1.10.1 + CUDA 10.2!
pip install torch==1.10.1+cu102 torchvision==0.11.2+cu102 torchaudio==0.10.1 -f https://download.pytorch.org/whl/cu102/torch_stable.html

# Install the corresponding spconv version
pip install spconv-cu102
```

Install dependencies
Install the remaining dependencies and setup the OpenPCDet code
```bash
# Setup SharedArray (make sure in the same virtual env)
cd SharedNumpyArray
python setup.py develop
cd ../

# Some other dependencies
pip install numba==0.58.1 #python 3.8 and above
pip install open3d
pip install mayavi

# Finally, setup the openpcdet (which will auto install the remaining dependencies)
python setup.py develop
```


## Troubleshooting

1. SharedArray is not supported in windows
2. 1.10.1 + CUDA 10.2
