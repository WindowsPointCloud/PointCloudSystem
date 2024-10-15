# PointCloudSystem

<!-- https://medium.com/@samunyi90/how-to-make-custom-language-badges-for-your-profile-using-shields-io-ec69ea95dfc0 -->
[![](https://img.shields.io/badge/Windows-10-0078D6?style=flat-square&logo=Windows)](https://www.microsoft.com/en-us/windows/)
[![](https://img.shields.io/badge/Cuda-10.2-6B8E23?style=flat-square&logo=Nvidia)](https://developer.nvidia.com/cuda-10.2-download-archive?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exelocal)
[![](https://img.shields.io/badge/Python-3.8-3776AB?style=flat-square&logo=Python)](https://www.python.org/)
[![](https://img.shields.io/badge/PyTorch-000000?style=flat-square&logo=PyTorch)](https://pytorch.org/)

## System
🤔 Installing OpenPCDet (and generally all other 3D object detection repositories) on a Windows device can be extremely tedious, as most of the open-source dependencies for OpenPCDet are not well-maintained on Windows. Therefore, we explicitly define our device system as follows for your reference:
1. Operating System (OS): Windows 10 Pro (version 22H2)
2. CUDA version: 10.2
3. Python version: 3.8
4. PyTorch version: 1.10.1
5. CPU: Intel(R) Xeon(R) E-2176G CPU @ 3.70GHz 

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
pip install spconv-cu102==2.3.6
```

Install the remaining dependencies and setup the OpenPCDet code
```bash
# Setup SharedArray (make sure in the same virtual env)
cd SharedNumpyArray
python setup.py develop
cd ../

# Some other dependencies
pip install numba==0.58.1 #python 3.8 and above
pip install open3d==0.18.0
pip install mayavi==4.8.2
pip install scipy==1.10.1
pip install scikit-image==0.21.0
pip install scikit-build==0.18.1

# Finally, setup the openpcdet (which will auto install the remaining dependencies)
python setup.py develop

# Lastly, rename SharedNumpyArray to SharedArray
python -c "import os; os.rename('SharedNumpyArray', 'SharedArray')"
```

Check if installation is succesful. You should see a GUI appear if no problem occurs.
```
cd tools
python demo.py --cfg_file "cfgs\kitti_models\pointpillar.yaml" --ckpt "..\data\kitti\pointpillar_7728.pth" --data_path "..\data\kitti\000000.bin"
cd ../
```


## Troubleshooting

### 1. GPU requirements
- As pointed out by [this comment](https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-979906767), you need a GPU with the Pascal architecture.
- Any newer architecture should be workable as well (so far we tested only in RTX2070)

### 2. SharedArray
- SharedArray is not supported on Windows OS, as pointed out by multiple [GitHub issues](https://github.com/open-mmlab/OpenPCDet/issues/1043#issue-1315948545).
- Fortunately, we found a GitHub implementation called [SharedNumpyArray](https://github.com/imaginary-friend94/SharedNumpyArray) that works for Windows OS.
- We integrated the entire library into this repo as `PointCloudSystem/SharedNumpyArray`, to avoid version incompatibility issues.
- Please follow the setup instructions as pointed above to setup the `SharedNumpyAray`, and rename it as `SharedArray` so that it can works like an actual SharedArray module.

### 3. iou3d windows build compatibility errors
- Interestingly, the iou3d codes in OpenPCDet could not work in Windows OS.
- The solution is pointed out by this [pull request](https://github.com/open-mmlab/OpenPCDet/pull/1040#issue-1315829406).
- Please note that the pull request has not been merged. It is possible that the pull request was not merged to avoid potential issues on Linux/Ubuntu, rather than due to any faults in the solution itself.
- Specifically, we follow the authors and made the following modification as shown [here](https://github.com/yihuajack/OpenPCDet/commit/fe62793d9362b5c794724c3eaf83ddd7db7b23ce)
- Modify your `pcdet/ops/iou3d_nms/src/iou3d_nms.cpp` and `pcdet/ops/iou3d_nms/src/iou3d_nms_kernel.cu` files following the provided suggestions.

### 4. Change `long` type -> `int32_t` type & Change `float` type -> `constexpr float` type
- This issue is the same problem caused by Troubleshoot Item 3 (iou3d windows build compatibility errors).
- We explicitly show the troubleshooting steps here, in case there is unknown sources of error.
- Basically, just change the data types in `pcdet/ops/iou3d_nms/src/iou3d_nms.cpp` and `pcdet/ops/iou3d_nms/src/iou3d_nms_kernel.cu` files.
- This issue is pointed by [this comment](https://github.com/open-mmlab/OpenPCDet/pull/1040#issue-1315829406), [that comment](https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-981505598), and also [this pull request](https://github.com/yihuajack/OpenPCDet/commit/fe62793d9362b5c794724c3eaf83ddd7db7b23ce).
- It is unsure if other .cpp code has this problem, but if similar problem arises, then please make the changes.
- You do not have to change `unsigned long long` type, it seems like no issue arise from this data type.

### 5. EPS error (i.e. "EPS" is undefined in device code)
- Unfortunately, we forgot how we resolve this problem.
- If we are not mistaken, fixing the iou3d and the data type as pointed by the Troubleshoot Item 3 and Troubleshoot Item 4 will resolve this problem.
- Else, you can also try changing the code as pointed out by [this comment](https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-1126938200)
- Inside `pcdet/ops/iou3d_nms/src/iou3d_cpu.cpp`, add this code `const double EPS=1E-8;`. Or you can also try with `const double EPS=1E-9;`

### NMS .py

## Miscellaneous
1. SharedArray is not supported on Windows OS, as pointed out by multiple [GitHub issues](https://github.com/open-mmlab/OpenPCDet/issues/1043#issue-1315948545). Fortunately, we found a GitHub implementation called [SharedNumpyArray](https://github.com/imaginary-friend94/SharedNumpyArray) that works for Windows OS. We integrated the entire library into this repo as `PointCloudSystem/SharedNumpyArray`, to avoid version incompatibility issues. Please follow the setup instructions as pointed above to setup the `SharedNumpyAray`, and rename it as `SharedArray` so that it can works like an actual SharedArray module.
2. If you want to update SpConv (whether it is an upgrade or downgrade), make sure you UNINSTALL the current version first!
3. 1.10.1 + CUDA 10.2

int/long type for iou3d
https://github.com/open-mmlab/OpenPCDet/pull/1040#issue-1315829406
https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-981505598
https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-981607892
https://github.com/yihuajack/OpenPCDet/commit/fe62793d9362b5c794724c3eaf83ddd7db7b23ce

EPS
https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-979801312
https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-1126938200

so we used
https://github.com/yihuajack/OpenPCDet as base


maybe can use 10.2
https://github.com/open-mmlab/OpenPCDet/issues/421#issue-777529509

SharedArray is not support in window OS
https://github.com/open-mmlab/OpenPCDet/issues/1043#issue-1315948545
So we use
https://github.com/imaginary-friend94/SharedNumpyArray
