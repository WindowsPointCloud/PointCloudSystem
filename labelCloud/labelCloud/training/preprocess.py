import open3d as o3d
import numpy as np
import os
import shutil
import json
import copy
from tqdm import tqdm

def preprocess_point_clouds(input_dir, output_dir):
    """
    Preprocess point cloud files by downsampling and filtering outliers.

    Parameters:
    - input_dir: str, directory containing the input .ply files.
    - output_dir: str, directory to save the preprocessed .ply files.
    """

    file_names = os.listdir(input_dir)

    # if output directory doesn't exist
    if not os.path.isdir(output_dir):
        # Create the output directory
        os.makedirs(output_dir, exist_ok=False)

        for idx in tqdm(range(len(file_names)), desc='Preprocessing (downsample + filter) input data...'):
            file_name = file_names[idx]
            file_path = os.path.join(input_dir, file_name)
            save_path = os.path.join(output_dir, file_name)

            if not file_name.endswith('.ply'):
                continue

            pcd = o3d.io.read_point_cloud(file_path)

            uni_down_pcd = pcd.uniform_down_sample(every_k_points=8)
            cl, ind = uni_down_pcd.remove_statistical_outlier(nb_neighbors=5, std_ratio=1.0)

            inlier_cloud = uni_down_pcd.select_by_index(ind)  # filter out inliers

            inlier_cloud_np = np.array(inlier_cloud.points)
            filtered_pcd = o3d.geometry.PointCloud()  # create a point cloud object to store the filtered points
            filtered_pcd.points = o3d.utility.Vector3dVector(inlier_cloud_np)  # Pass xyz to Open3D.o3d.geometry.PointCloud

            o3d.io.write_point_cloud(save_path, filtered_pcd)  # save the filtered point cloud
    else:
        print('Apparently, you have preprocessed the input data previously! Please check')


def split_and_crop_point_clouds(ply_dir, label_dir):
    """
    Split and crop point cloud files and corresponding label files.

    Parameters:
    - ply_dir: str, directory containing the input .ply files.
    - label_dir: str, directory containing the label files (json format).
    """

    file_names = sorted(os.listdir(ply_dir))

    if "part1" in file_names[0] or "part2" in file_names[0]:
        print('Apparently, you have split & cropped the preprocessed data previously! Please check')
        return

    for idx in tqdm(range(len(file_names)), desc='Splitting and cropping the RoI of input data...'):
        ####################################
        # Split data (ply)
        ####################################
        file_name = file_names[idx]
        if not file_name.endswith('.ply'):
            continue
        file_path = os.path.join(ply_dir, file_name)
        save_path_1 = os.path.join(ply_dir, file_name.replace(".ply", "_part1.ply"))
        save_path_2 = os.path.join(ply_dir, file_name.replace(".ply", "_part2.ply"))
        save_paths = [save_path_1, save_path_2]

        pcd = o3d.io.read_point_cloud(file_path)
        inlier_cloud_np = np.array(pcd.points)  # the loaded is already inlier clouds, filtered in batch_preprocess.py

        # Split into half
        x_range = 5.13  # the ROI is fixed, don't use np.max(inlier_cloud_np[:,0]) + np.min(inlier_cloud_np[:,0])
        x_mid_thresh = x_range / 2
        x_min_thresh = 0.23
        x_max_thresh = 0.77

        part_1 = inlier_cloud_np[inlier_cloud_np[:, 0] > x_mid_thresh]
        part_1 = part_1[part_1[:, 0] < x_max_thresh * x_range]
        part_1[:, 0] = part_1[:, 0] - x_mid_thresh  # update the xyz value in point cloud itself

        part_2 = inlier_cloud_np[inlier_cloud_np[:, 0] <= x_mid_thresh]
        part_2 = part_2[part_2[:, 0] > x_min_thresh * x_range]
        part_2[:, 0] = part_2[:, 0] - x_min_thresh * x_range  # update the xyz value in point cloud itself

        inlier_cloud_nps = [part_1, part_2]

        # Save
        for inlier_cloud_np, save_path in zip(inlier_cloud_nps, save_paths):
            splitted_pcd = o3d.geometry.PointCloud()  # create a point cloud object to store the filtered points
            splitted_pcd.points = o3d.utility.Vector3dVector(inlier_cloud_np)  # Pass xyz to Open3D.o3d.geometry.PointCloud

            o3d.io.write_point_cloud(save_path, splitted_pcd)  # save the filtered point cloud

        # Remove original (non-split .ply file)
        os.remove(file_path)

        ####################################
        # Split label (json) if available
        ####################################
        try:
            ori_label_path = os.path.join(label_dir, file_name.replace(".ply", ".json"))
            label_path_1 = os.path.join(label_dir, file_name.replace(".ply", "_part1.json"))
            label_path_2 = os.path.join(label_dir, file_name.replace(".ply", "_part2.json"))
            label_paths = [label_path_1, label_path_2]

            # Read original label json
            with open(ori_label_path) as f:
                data = json.load(f)

            # Modify the label accordingly
            objs = data['objects']
            objs_part_1 = []
            objs_part_2 = []
            for obj in objs:
                if obj['centroid']['x'] > x_mid_thresh:
                    obj['centroid']['x'] = obj['centroid']['x'] - x_mid_thresh
                    objs_part_1.append(obj)
                else:
                    obj['centroid']['x'] = obj['centroid']['x'] - x_min_thresh * x_range
                    objs_part_2.append(obj)
            splitted_objs = [objs_part_1, objs_part_2]

            # Save
            for i, (label_path, objs) in enumerate(zip(label_paths, splitted_objs)):
                new_data = copy.deepcopy(data)
                new_data['objects'] = objs
                new_data['filename'] = new_data['filename'].replace(".ply", f"_part{i+1}.ply")
                new_data['path'] = new_data['path'].replace(".ply", f"_part{i+1}.ply")

                with open(label_path, 'w') as f:
                    json.dump(new_data, f, indent=4)

            # Remove original
            os.remove(ori_label_path)
        except Exception as e:
            print(e)


# write a json file
def write_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def read_all_json_files(label_dir, ply_dir):
    file_list = os.listdir(label_dir)
    file_list.sort()
    data_list = []
    for file in file_list:
        if file == '_classes.json':
            print('skip _classes.json')
            continue
        file_path = os.path.join(label_dir, file)
        data = read_json_file(file_path)

        # modify the folder that contains the ply file
        data['folder'] = ply_dir

        # modify the label path
        path = data['path']
        if len(data['objects']) == 0:
            print(f"Remove empty file {file_path}")
            os.remove(file_path)
            continue
        # get the filename without parents directory
        path = path.split('/')[-1]
        path = os.path.join(os.getcwd(), ply_dir, path)
        data['path'] = path
        # write to json file using write_json_file
        write_json_file(file_path, data)
