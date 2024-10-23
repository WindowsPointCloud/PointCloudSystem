import argparse
import glob
import pandas as pd
from pathlib import Path
from plyfile import PlyData
import json
try:
    import open3d
    from visual_utils import open3d_vis_utils as V
    OPEN3D_FLAG = True
except:
    import mayavi.mlab as mlab
    from visual_utils import visualize_utils as V
    OPEN3D_FLAG = False

import numpy as np
import torch
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from pcdet.config import cfg, cfg_from_yaml_file
from pcdet.datasets import DatasetTemplate
from pcdet.models import build_network, load_data_to_gpu
from pcdet.utils import common_utils



class DemoDataset(DatasetTemplate):
    def __init__(self, dataset_cfg, class_names, training=True, root_path=None, logger=None, ext='.bin'):
        """
        Args:
            root_path:
            dataset_cfg:
            class_names:
            training:
            logger:
        """
        super().__init__(
            dataset_cfg=dataset_cfg, class_names=class_names, training=training, root_path=root_path, logger=logger
        )
        self.root_path = root_path
        self.ext = ext
        data_file_list = glob.glob(str(root_path / f'*{self.ext}')) if self.root_path.is_dir() else [self.root_path]

        data_file_list.sort()
        self.sample_file_list = data_file_list

    def __len__(self):
        return len(self.sample_file_list)

    def __getitem__(self, index):
        if self.ext == '.bin':
            points = np.fromfile(self.sample_file_list[index], dtype=np.float32).reshape(-1, 4)
        elif self.ext == '.npy':
            points = np.load(self.sample_file_list[index])
        elif self.ext == '.ply':
            ply_file = self.sample_file_list[index]
            # Convert ply to bin object without saving
            points = self.convert_ply_to_bin_object(ply_file)
            
        else:
            raise NotImplementedError

        input_dict = {
            'points': points,
            'frame_id': index,
        }

        data_dict = self.prepare_data(data_dict=input_dict)
        return data_dict
        
    @staticmethod
    def convert_ply_to_bin_object(input_path, pc_mf = 20):
        # read data
        plydata = PlyData.read(input_path)
        data = plydata.elements[0].data
        # convert to DataFrame
        data_pd = pd.DataFrame(data)
        # convert rgb to intensity 
        data_pd['intensity'] = 0
        try:
            data_pd = data_pd.drop('red', axis=1)
            data_pd = data_pd.drop('green', axis=1)
            data_pd = data_pd.drop('blue', axis=1)
        except:
            pass
        # x 100
        data_pd['x'] = data_pd['x'].map(lambda x: x * pc_mf)
        data_pd['y'] = data_pd['y'].map(lambda x: x * pc_mf)
        data_pd['z'] = data_pd['z'].map(lambda x: x * pc_mf)
        # initialize array to store data
        data_np = np.zeros(data_pd.shape, dtype=float)
        # read names of properties
        property_names = list(data_pd.columns)
        # read data by property
        for i, name in enumerate(property_names): 
            data_np[:, i] = data_pd[name]
        return data_np.astype(float).reshape(-1, 4)



def parse_config():
    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('--cfg_file', type=str, default='cfgs/kitti_models/second.yaml',
                        help='specify the config for demo')
    parser.add_argument('--data_path', type=str, default='demo_data',
                        help='specify the point cloud data file or directory')
    parser.add_argument('--ckpt', type=str, default=None, help='specify the pretrained model')
    parser.add_argument('--ext', type=str, default='.bin', help='specify the extension of your point cloud data file')
    parser.add_argument('--saved_prediction_label_directory', type=str, default='saved_predictions',
                        help='directory to save prediction labels')
    parser.add_argument('--truth_label_directory', type=str, default=None,
                        help='directory containing ground truth labels')
    parser.add_argument('--visualize_2d', action='store_true', help='whether to visualize in 2D bird eye view')

    args = parser.parse_args()

    cfg_from_yaml_file(args.cfg_file, cfg)

    return args, cfg

def save_predictions_to_csv(pred_dicts, file_name):
    # Convert predictions to a DataFrame and save as CSV
    columns = ['x', 'y', 'z', 'dx', 'dy', 'dz', 'rot', 'cls', 'conf']
    pred_list = []
    for i in range(len(pred_dicts[0]['pred_boxes'])):
        x, y, z, dx, dy, dz, rot = pred_dicts[0]['pred_boxes'][i][:7]
        cls = int(pred_dicts[0]['pred_labels'][i])
        conf = float(pred_dicts[0]['pred_scores'][i])
        pred_list.append([x, y, z, dx, dy, dz, rot, cls, conf])
    
    df = pd.DataFrame(pred_list, columns=columns)
    df.to_csv(file_name, index=False)


def visualize_2d_bird_eye(points, pred_boxes, saved_prediction_label_directory, truth_boxes=None, file_name="Visualization"):
    # Create figure and axis
    if truth_boxes is not None:
        fig, axs = plt.subplots(1, 2, figsize=(20, 10))
        fig.suptitle(file_name)
        # Plot with prediction labels
        axs[0].scatter(points[:, 0], points[:, 1], s=0.1, c=points[:, 2], cmap='viridis')
        axs[0].set_xlim(-5, 32)
        axs[0].set_ylim(-5, 25)
        axs[0].set_title("Bird's Eye View with Prediction Labels")
        
        for box in pred_boxes:
            x, y, z, dx, dy, dz, rot, cls, conf = box
            if conf < 0.2:
                continue
            bottom_left_x = x - dx / 2
            bottom_left_y = y - dy / 2
            rot = rot * 57.2957795  # rad to degree
            color = 'blue' if cls == 1 else 'red'
            rectangle = patches.Rectangle((bottom_left_x, bottom_left_y), dx, dy, angle=rot, rotation_point="center",
                                          color=color, fill=False)
            axs[0].add_patch(rectangle)

        # Plot with truth labels
        axs[1].scatter(points[:, 0], points[:, 1], s=0.1, c=points[:, 2], cmap='viridis')
        axs[1].set_xlim(-5, 32)
        axs[1].set_ylim(-5, 25)
        axs[1].set_title("Bird's Eye View with Truth Labels")
        
        for box in truth_boxes:
            
            x, y, z, dx, dy, dz, rot, cls = box
            bottom_left_x = x - dx / 2
            bottom_left_y = y - dy / 2
            rot = rot * 57.2957795  # rad to degree
            color = 'blue'
            rectangle = patches.Rectangle((bottom_left_x, bottom_left_y), dx, dy, angle=rot, rotation_point="center",
                                          color=color, fill=False)
            axs[1].add_patch(rectangle)
    
    else:
        fig, ax = plt.subplots(figsize=(20, 10))
        fig.suptitle(file_name)
        # Plot the point cloud (Bird's Eye View)
        ax.scatter(points[:, 0], points[:, 1], s=0.1, c=points[:, 2], cmap='viridis')
        ax.set_xlim(-5, 32)
        ax.set_ylim(-5, 25)
        ax.set_title("Bird's Eye View of Point Cloud with Bounding Boxes")
        
        # Plot predicted bounding boxes
        for box in pred_boxes:
            x, y, z, dx, dy, dz, rot, cls, conf = box
            if conf < 0.2:
                continue
            bottom_left_x = x - dx / 2
            bottom_left_y = y - dy / 2
            rot = rot * 57.2957795  # rad to degree
            color = 'red' if cls == 1 else 'blue'
            rectangle = patches.Rectangle((bottom_left_x, bottom_left_y), dx, dy, angle=rot, rotation_point="center",
                                          color=color, fill=False)
            ax.add_patch(rectangle)
            
    plot_file_path = Path(saved_prediction_label_directory) / f"{file_name}_bird_eye_view.png"
    plt.savefig(plot_file_path)
    plt.show()
    
def main():
    args, cfg = parse_config()
    logger = common_utils.create_logger()
    logger.info('-----------------Quick Demo of OpenPCDet-------------------------')
    demo_dataset = DemoDataset(
        dataset_cfg=cfg.DATA_CONFIG, class_names=cfg.CLASS_NAMES, training=False,
        root_path=Path(args.data_path), ext=args.ext, logger=logger
    )
    logger.info(f'Total number of samples: \t{len(demo_dataset)}')

    model = build_network(model_cfg=cfg.MODEL, num_class=len(cfg.CLASS_NAMES), dataset=demo_dataset)
    model.load_params_from_file(filename=args.ckpt, logger=logger, to_cpu=True)
    model.cuda()
    model.eval()
    
    # Create the prediction label directory if it doesn't exist
    Path(args.saved_prediction_label_directory).mkdir(parents=True, exist_ok=True)

    with torch.no_grad():
        for idx, data_dict in enumerate(demo_dataset):
            logger.info(f'Visualized sample index: 	{idx + 1}')
            data_dict = demo_dataset.collate_batch([data_dict])
            load_data_to_gpu(data_dict)
            pred_dicts, _ = model.forward(data_dict)

            # Save predictions to CSV file
            if Path(args.data_path).is_dir():
                input_file_name = Path(demo_dataset.sample_file_list[idx]).stem
                pred_file_path = Path(args.saved_prediction_label_directory) / f"{input_file_name}_pred.csv"
            else:
                pred_file_path = Path(args.saved_prediction_label_directory) / f"{Path(args.data_path).stem}_pred.csv"
                input_file_name = Path(args.data_path).stem
            save_predictions_to_csv(pred_dicts, pred_file_path)

            if args.visualize_2d:
                points = data_dict['points'][:, 1:].cpu().numpy()
                pred_boxes = np.concatenate((pred_dicts[0]['pred_boxes'].cpu(), 
                                             pred_dicts[0]['pred_labels'].cpu().reshape(-1, 1), 
                                             pred_dicts[0]['pred_scores'].cpu().reshape(-1, 1)), axis=1)
                
                truth_boxes = None
                if args.truth_label_directory:
                    pc_mf = 20 if args.ext == '.ply' else 1
                    truth_file_path = Path(args.truth_label_directory) / f"{input_file_name}.json"
                    if truth_file_path.exists():
                        with open(truth_file_path, 'r') as f:
                            truth_data = json.load(f)
                            truth_boxes = []
                            for obj in truth_data['objects']:
                                x = obj['centroid']['x'] *pc_mf
                                y = obj['centroid']['y'] *pc_mf
                                z = obj['centroid']['z'] *pc_mf
                                dx = obj['dimensions']['length'] *pc_mf
                                dy = obj['dimensions']['width'] *pc_mf
                                dz = obj['dimensions']['height'] *pc_mf
                                rot = obj['rotations']['z']
                                cls = 1 if obj['name'] == 'good' else 2
                                truth_boxes.append([x, y, z, dx, dy, dz, rot, cls])
                
                visualize_2d_bird_eye(points, pred_boxes, args.saved_prediction_label_directory, truth_boxes, file_name=input_file_name)
            elif OPEN3D_FLAG:
                V.draw_scenes(
                    points=data_dict['points'][:, 1:], ref_boxes=pred_dicts[0]['pred_boxes'],
                    ref_scores=pred_dicts[0]['pred_scores'], ref_labels=pred_dicts[0]['pred_labels']
                )
                
  


                if not OPEN3D_FLAG:
                    mlab.show(stop=True)

    logger.info('Demo done.')


if __name__ == '__main__':
    main()
