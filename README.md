# PointCloudSystem


## Setup
Conda environment
```bash
conda create --name windowpointcloud python=3.8 -y
conda activate windowpointcloud

git clone https://github.com/WindowPointCloud/PointCloudSystem.git
cd PointCloudSystem
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
