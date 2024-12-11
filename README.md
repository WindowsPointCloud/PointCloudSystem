# PointCloudSystem

<!-- https://medium.com/@samunyi90/how-to-make-custom-language-badges-for-your-profile-using-shields-io-ec69ea95dfc0 -->
[![](https://img.shields.io/badge/Windows-10-0078D6?style=flat-square&logo=Windows)](https://www.microsoft.com/en-us/windows/)
[![](https://img.shields.io/badge/Cuda-11.6-6B8E23?style=flat-square&logo=Nvidia)](https://developer.nvidia.com/cuda-11.6-download-archive?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exelocal)
[![](https://img.shields.io/badge/Python-3.8-3776AB?style=flat-square&logo=Python)](https://www.python.org/)
[![](https://img.shields.io/badge/PyTorch-000000?style=flat-square&logo=PyTorch)](https://pytorch.org/)

## 📚 Module Overview

Most existing point cloud detection frameworks are implemented and optimized for Linux/Ubuntu systems, including our preferred OpenPCDet framework. Therefore, this framework is a point cloud object detection system (`PointCloudSystem`) dedicated to `Windows OS`. It covers end-to-end functionalities from data annotation, data preprocessing, data augmentation, to training and testing. Specifically, we integrate `labelCloud` and `OpenPCDet` into this framework for annotation and training, respectively. Additionally, we incorporate our custom data preprocessing and augmentation pipeline to facilitate the end-to-end process. The details of the flowchart are provided below:

```
# Preprocessing Module (tools/batch_preprocess.py)
DataPreprocessor.run() 
    ↓
  downsample() 
    ↓
  split_points() 
    ↓
  modify_labels()

# Augmentation Module (tools/batch_augment.py)
AugmentationThread.run_augmentation() 
    ↓
  augment()

# Training Module (tools/batch_train.py)
TrainingThread.run()
    ↓
  python convert_raw_data.py 
    ↓
  python train.py

# Testing and Inference Module (tools/batch_test.py)
TestingThread.run()
```

### 📋 Table of content
 1. [System Requirement](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/README.md#-system-requirement)
 2. [Setup](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/README.md#-setup)
 3. [Run the GUI](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/README.md#%EF%B8%8F-run-the-gui)
 4. [Convert labelCloud.py to .exe](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/README.md#-convert-labelcloudpy-to-exe)
 5. [Sample Training Results](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/README.md#-sample-training-results)
 6. [Troubleshooting](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/README.md#-troubleshooting)
 7. [Miscellaneous](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/README.md#-miscellaneous)



## 📝 System Requirement 
Installing OpenPCDet (and generally all other 3D object detection repositories) on a Windows device can be extremely tedious 🤔, as most of the open-source dependencies for OpenPCDet are not well-maintained on Windows. Therefore, we explicitly define our device system as follows for your reference:
1. Operating System (OS): Windows 10 Pro (version 22H2)
2. CUDA version: 11.6
3. Python version: 3.8
4. PyTorch version: 1.13.1
5. CPU: Intel(R) Xeon(R) E-2176G CPU @ 3.70GHz
6. Microsoft Visual Studio 2019

So far, we have been able to reimplement this repository as long as the following system conditions are met. Ensure you are using Windows 10 and CUDA 11.6. We will guide you through setting up the remaining Python dependencies in the next section.

## ⌛ Setup
Please follow the sequence! ⚠️ Any other sequence may result in unknown errors which no one has solved before.

Prerequisites
1. Install the appropriate version of CUDA (CUDA 11.6 in our case), then set the path correctly in the environment variables following our guides [here](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/documentations/Swap_CUDA_Version.md) if you have multiple CUDA versions.
2. Install the appropriate version of Microsoft Visual Studio (2019 version in our case), then set the path correctly in the environment variables following our guides [here](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/documentations/Configure_Microsoft_Visual_Studio_Path.md).

Conda environment
```bash
conda create --name windowspointcloud python=3.8 -y
conda activate windowspointcloud

git clone https://github.com/WindowsPointCloud/PointCloudSystem.git
cd PointCloudSystem
```

Install pytorch and spconv. Find the installation command via [pytorch get started](https://pytorch.org/get-started/previous-versions/) and [spconv repo](https://github.com/traveller59/spconv)
```
# Install torch version 1.13.1 + CUDA 11.6!
pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116

# Install the corresponding spconv version
pip install spconv-cu116==2.3.6
```

Install the remaining dependencies and setup the OpenPCDet code
```bash
# Setup SharedArray (make sure in the same virtual env)
cd SharedNumpyArray
python setup.py develop
cd ../

# Some other dependencies
pip install numba==0.52.0
pip install numpy==1.20.3
pip install open3d==0.18.0
pip install mayavi==4.8.2
pip install scipy==1.10.1
pip install scikit-image==0.21.0
pip install scikit-build==0.18.1

# Setup OpenPCDet
python setup.py develop

# Install the remaining dependencies
pip install pandas==1.5.3
pip install plyfile==1.0.1
pip install opencv-python==4.7.0.72
pip install av2==0.2.1
pip install kornia==0.5.8
pip install mayavi==4.8.2
pip install PyQt5==5.15.9
pip install open3d==0.18.0
pip install chardet==5.2.0

# Fix some of the dependencies to certain version
pip install numpy==1.20.3
pip install pillow==9.0.1
pip install PyOpenGL==3.1.0
pip install --no-binary=PyOpenGL_accelerate PyOpenGL_accelerate
pip install configobj==5.0.9
pip install mayavi==4.8.2
pip install nptyping==2.5.0

# Encouraged: To fix rotate_iou.py openpcdet numba.cuda.cudadrv.error.NvvmError: Failed to compile
pip uninstall numba==0.52.0
pip uninstall numpy==1.20.3
pip install numpy==1.20.3
pip install numba==0.53.0

# To edit the BASE_CONFIG path automatically in the pointpillar.yaml file
pip install ruamel.yaml==0.18.6

# Lastly, rename SharedNumpyArray to SharedArray
python -c "import os; os.rename('SharedNumpyArray', 'SharedArray')"
```

Check if installation is succesful. You should see a GUI appear if no problem occurs.
```
cd tools
python demo.py --cfg_file "cfgs\kitti_models\pointpillar.yaml" --ckpt "..\data\kitti\pointpillar_7728.pth" --data_path "..\data\kitti\000000.bin"
cd ../
```

## 🖥️ Run the GUI
Go to the `labelCloud` directory if you haven't already
```
cd PointCloudSystem
cd labelCloud
```

Run the `labelCloud.py`
```
python labelCloud.py
```

## 🔁 Convert labelCloud.py to .exe
Go to the `labelCloud` directory if you haven't already
```
cd PointCloudSystem
cd labelCloud
```

Install pyinstaller
```
pip install pyinstaller
```

Convert labelCloud.py to .exe
```
pyinstaller --onefile --noconsole --icon=your_icon.ico labelCloud.py

or

pyinstaller --onefile --noconsole labelCloud.py
```

You should get a file called `labelCloud.spec` after conversion. Open the .spec file, and add this `datas` into the file. Make sure you change the parent path accordingly. You can refer this [image](https://github.com/user-attachments/assets/fae53c29-aa42-4ff7-b1fb-20ab135d4edb) as reference of how to put the `datas` into `labelCloud.spec` file.
```
       datas=[
	  ('D:\\Hum\\PointCloudSystem\\labelCloud\\labelCloud\\resources\\interfaces\\*.ui', 'resources/interfaces'),
      ('D:\\Hum\\PointCloudSystem\\labelCloud\\labelCloud\\resources\\icons\\*.ico', 'resources/icons'),
	  ('D:\\Hum\\PointCloudSystem\\labelCloud\\labelCloud\\resources\\icons\\*.svg', 'resources/icons'),
	   ('C:\\Users\\user\\anaconda3\\envs\\windowspointcloud\\Lib\\site-packages\\cumm\\include', 'cumm/include'),
	],
```

Convert again to make sure the pyinstaller take account into our dependencies listed in the `datas` in `labelCloud.spec`.
```
pyinstaller labelCloud.spec
```

Now, you should get a `/dist` folder inside `PointCloudSystem/labelCloud`. Inside the `/dist` folder, you should have the `labelCloud.exe`. Copy the `labelCloud.exe` and paste it inside `PointCloudSystem/labelCloud`, alongside with your `labelCloud.py`. The tree directory should look something as follows:
``` 
PointCloudSystem/labelCloud
├── dist
│   ├── labelCloud.exe
│   ├── [and other files and directories ...]
├── labelCloud.exe
├── labelCloud.py
├── labelCloud.spec
└── ...
```

## 📊 Sample Training Results

<table border="1">
  <tr>
    <th rowspan="2">Backbone</th>
    <th colspan="3">Exclude Augmented Data in Test Set</th>
    <th colspan="3">Include Augmented Data in Test Set</th>
  </tr>
  <tr>
    <td>AP (Pass)</td>
    <td>AP (Fail)</td>
    <td>Recall</td>
    <td>AP (Pass)</td>
    <td>AP (Fail)</td>
    <td>Recall</td>
  </tr>
  <tr>
    <td>PointPillar</td>
    <td>99.88</td>
    <td>78.53</td>
    <td>93.16</td>
    <td>99.61</td>
    <td>98.35</td>
    <td>88.50</td>
  </tr>
  <tr>
    <td>PV-RCNN</td>
    <td>82.47</td>
    <td>16.17</td>
    <td>78.48</td>
    <td>82.47</td>
    <td>51.37</td>
    <td>71.84</td>
  </tr>
</table>



## 🛠 Troubleshooting

Here, we share our troubleshooting and debugging process for the purpose of experience sharing. Specifically, these troubleshooting steps are what we summarized after migrating the original OpenPCDet from Linux/Ubuntu to Windows OS. Ideally, this codebase should work if you installed it following our [system requirements](https://github.com/WindowsPointCloud/PointCloudSystem/blob/main/README.md#-system-requirement). However, you might have a different hardware system, which might require another set of software dependencies. If so, you might need to adjust some of the software dependencies based on our troubleshooting summary. We hope this sharing helps with your installation on Windows OS!

### 1. GPU requirements
- As pointed out by [this comment](https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-979906767), you need a GPU with the Pascal architecture or newer.
- Any newer architecture should be workable as well (so far we tested only in RTX2070)

### 2. CUDA and PyTorch version
- Due to unknown reasons, only a few CUDA + PyTorch combinations can work for OpenPCDet.
- According to one [comment](https://github.com/open-mmlab/OpenPCDet/issues/421#issue-777529509) and many more (which we have lost track), it seems that CUDA 10.2 is the most stable version, with more successful installations on Windows.
- `Updates 1`: We found that OpenPCDet recommends using `torch<=1.10`, which is only supported by the older CUDA versions. One of the CUDA versions which support the older torch version is `CUDA 10.2`. However, Linux/Ubuntu users may not face as many issues compared to Windows user. But the issues are manageable following our troubleshooting guides below.
- `Updates 2`: Other than `CUDA 10.2`, we added a branch to this repo for `CUDA 11.6` using `torch==1.13.1`

### 3. Numba and Numpy version
- You can find the Numba and Numpy compatibility for different Python versions in [this link](https://numba.readthedocs.io/en/stable/user/installing.html)
- However, Numba and Numpy version might sometimes also clash due to unknown reason (this problem is less usual in Linux/Ubuntu)
- After some trial-and-error, we set `numpy==1.20.3` while numba version may be `numba==0.52.0` or `numba==0.53.0`, depending on CUDA 10.2 or CUDA 11.6.
- ⚠️ Note that the original numpy code in OpenPCDet is written for version 1.24 and above, so we have to modify quite some code in the OpenPCDet for compatbility.
- We do not show every files that require modifications, but it is pretty straightforward. Our codebase has been updated with numpy codes for version 1.20.

### 4. SharedArray
- SharedArray is not supported on Windows OS, as pointed out by multiple [GitHub issues](https://github.com/open-mmlab/OpenPCDet/issues/1043#issue-1315948545).
- Fortunately, we found a GitHub implementation called [SharedNumpyArray](https://github.com/imaginary-friend94/SharedNumpyArray) that works for Windows OS.
- We integrated the entire library into this repo as `PointCloudSystem/SharedNumpyArray`, to avoid version incompatibility issues.
- Please follow the setup instructions as pointed above to setup the `SharedNumpyAray`, and rename it as `SharedArray` so that it can works like an actual SharedArray module.

### 5. iou3d windows build compatibility errors
- Interestingly, the iou3d codes in OpenPCDet could not work in Windows OS.
- The solution is pointed out by this [pull request](https://github.com/open-mmlab/OpenPCDet/pull/1040#issue-1315829406).
- Please note that the pull request has not been merged. It is possible that the pull request was not merged to avoid potential issues on Linux/Ubuntu, rather than due to any faults in the solution itself.
- Specifically, we follow the authors and made the following modification as shown [here](https://github.com/yihuajack/OpenPCDet/commit/fe62793d9362b5c794724c3eaf83ddd7db7b23ce)
- Modify your `pcdet/ops/iou3d_nms/src/iou3d_nms.cpp` and `pcdet/ops/iou3d_nms/src/iou3d_nms_kernel.cu` files following the provided suggestions.

### 6. Change `long` type -> `int32_t` type & Change `float` type -> `constexpr float` type
- This issue is the same problem caused by Troubleshoot Item 5 (iou3d windows build compatibility errors).
- We explicitly show the troubleshooting steps here, in case there is unknown sources of error.
- Basically, just change the data types in `pcdet/ops/iou3d_nms/src/iou3d_nms.cpp` and `pcdet/ops/iou3d_nms/src/iou3d_nms_kernel.cu` files.
- This issue is pointed by [this comment](https://github.com/open-mmlab/OpenPCDet/pull/1040#issue-1315829406), [that comment](https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-981505598), and also [this pull request](https://github.com/yihuajack/OpenPCDet/commit/fe62793d9362b5c794724c3eaf83ddd7db7b23ce). The explanation is provided [here](https://github.com/open-mmlab/OpenPCDet/issues/1287#issue-1616648384)
- It is unsure if other .cpp code has this problem, but if similar problem arises, then please make the changes.
- You do not have to change `unsigned long long` type, it seems like no issue arise from this data type.

### 7. EPS error (i.e. "EPS" is undefined in device code)
- Unfortunately, we forgot how we resolve this problem.
- If we are not mistaken, fixing the iou3d and the data type as pointed by the Troubleshoot Item 5 and Troubleshoot Item 6 will resolve this problem.
- Else, you can also try changing the code as pointed out by [this comment](https://github.com/open-mmlab/OpenPCDet/issues/681#issuecomment-1126938200)
- Inside `pcdet/ops/iou3d_nms/src/iou3d_cpu.cpp`, add this code `const double EPS=1E-8;`. Or you can also try with `const double EPS=1E-9;`

### 8. Torch `LongTensor type` is not working in `pcdet/ops/iou3d_nms/iou3d_nms_utils.py`
- Convert `torch.LongTensor` to `torch.IntTensor` in `pcdet/ops/iou3d_nms/iou3d_nms_utils.py`
- You can refer our modification [here](https://github.com/WindowsPointCloud/PointCloudSystem/commit/13358e8cf03f8598f45bc97fc9eecad60fa7e860#diff-5c8e037c9b0712fded73f29e7ef69db6c87088f0917b8a9b0887ae4f003be631R98)
- ⚠️ This might occur elsewhere, since our code is mainly just focused on `pointpillar` model.
- Generally, if any problems occur, consider changing `torch.LongTensor` to `torch.IntTensor`

### 9. How to change CUDA version in Windows?
- If you have more than one CUDA installed, then you might need to swap the environment variables to link the correct path of CUDA for the Windows system. Note that Windows may not automatically configure the path correctly when you install new CUDA, so please take note.
- Firstly, you can use this command `nvcc --version` to check the CUDA version. Note that `nvidia-smi` might show a different CUDA version. But we always follow the version showed by `nvcc --version`. You can refer [this explanation](https://stackoverflow.com/a/53504578) to understand more.
- If `nvcc --version` shows a version which is not the one you want, please refer the steps [here](documentations/Swap_CUDA_Version.md). A step-by-step guide is provided with screenshots to guide you.

### 10. Unsupported Microsoft Visual Studio version
- The complete error is `unsupported Microsoft Visual Studio version! Only the versions between 2017 and 2022 (inclusive) are supported! The nvcc flag '-allow-unsupported-compiler' can be used to override this version check; however, using an unsupported host compiler may cause compilation failure or incorrect run time execution. Use at your own risk.`
- Sometimes, you will face this error even if you are using the correct version. This is because you might have more than one installed version, and/or the environment variable `Path` is not configured correctly.
- To solve this, first make sure you had installed a Microsoft Visual Studio version between 2017 and 2022 (inclusive).
- Then, please follow our guide listed [here](documentations/Configure_Microsoft_Visual_Studio_Path.md).

### 11. subprocess.CalledProcessError: Command '['ninja', '-v']' returned non-zero exit status 1.
- When you are running `python setup.py develop` to setup OpenPCDet, you might face the above error.
- To solve this, open `PointCloudSystem/setup.py`
- Replace the code `BuildExtension` with `BuildExtension.with_options(use_ninja=False)`
- This should mitigate the problem.

### 12. fatal error: THC/THC.h: No such file or directory
- If we are not mistaken, this problem is likely to occur if you are using `torch>1.10`. That is why we set the torch version to `torch=1.10` for this repo. The reason is because OpenPCDet recommends using `torch<=1.10`.
- However, we found that newer CUDA versions do not support lower version torch. Hence, it is inevitable for most of us to use `torch>1.10`.
- To solve this, go to directory `PointCloudSystem/pcdet/ops/pointnet2/pointnet2_batch/src` and directory `PointCloudSystem/pcdet/ops/pointnet2/pointnet2_stack/src`. For each `.cpp` codes in these two directories, uncomment `include <THC/THC.h>` and `extern THCState *state;`. Example of uncommenting is shown below:</br></br>
![image](https://github.com/user-attachments/assets/74a2a32c-72b1-43de-b496-e061be0d3f9c)


### 13. rotate_iou.py openpcdet numba.cuda.cudadrv.error.NvvmError: Failed to compile
- If you face this issue, then most likely is your numba version is not compatible with your python version, numpy version , and (maybe) hardware.
- You can find the Numba and Numpy compatibility for different Python versions in [this link](https://numba.readthedocs.io/en/stable/user/installing.html)
- For CUDA 11.6 + python 3.8, then `numba==0.53.0` and `numpy==1.20.3` should work for you.

## 🧰 Miscellaneous

### 1. For other CUDA version(s):
- We tested the PointCloudSystem module on other CUDA version(s) as well. Note that for different CUDA version(s), you might need a slightly different installation process and slightly different codes. We have edited the relevant codes and provided the installation guide in the following branch(es).
- CUDA 10.2: [cuda102 branch](https://github.com/WindowsPointCloud/PointCloudSystem/tree/cuda102)

  
### 2. How to interpret the metrics
- Please refer [this explanation](https://github.com/open-mmlab/OpenPCDet/issues/432#issuecomment-808099795), which explains better than anyone else!
- We mostly follows the AP_R40@0.50 metric, which means the Average Precision at IoU thresholds 0.50, with 40 points approximation on the Precision-Recall curve.
- For recall, we follow the recall_rcnn_0.5, which is the overall recall (averaged across all classes) at IoU threshold of 0.5.

## Acknowledgements and References
We really appreciate the open-source community for coming up with solutions to the different problems we faced.
1. https://blog.csdn.net/weixin_49252254/article/details/135087124
2. https://github.com/Uzukidd/OpenPCDet-Win11-Compatible/blob/master/README.md
3. https://github.com/bycloudai/SwapCudaVersionWindows
4. https://github.com/yihuajack/OpenPCDet/commit/fe62793d9362b5c794724c3eaf83ddd7db7b23ce
5. https://github.com/imaginary-friend94/SharedNumpyArray
6. and etc (which we have quoted along throughout the README

<!--
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
-->
