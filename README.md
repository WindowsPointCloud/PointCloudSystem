# PointCloudSystem


## Setup
Conda environment
```bash
conda create --name windowpointcloud python=3.8 -y
conda activate windowpointcloud

git clone https://github.com/WindowPointCloud/PointCloudSystem.git
cd PointCloudSystem
```

Install pytorch and spconv
```
# Install torch version 1.10.1 + CUDA 10.2!
pip install torch==1.10.1+cu102 torchvision==0.11.2+cu102 torchaudio==0.10.1 -f https://download.pytorch.org/whl/cu102/torch_stable.html

# Install the corresponding spconv version
pip install spconv-cu102
```

Install dependencies
```bash
# Setup SharedArray
cd SharedNumpyArray
python setup.py develop (make sure in the same virtual env)
cd ../

# the remaining dependencies
pip install numba==0.58.1 #python 3.8 and above
pip install open3d
pip install mayavi
```


## Troubleshooting

1. SharedArray is not supported in windows
2. 
