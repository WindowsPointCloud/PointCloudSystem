import open3d as o3d
import numpy as np
import os
import shutil
from PyQt5.QtCore import QThread, pyqtSignal
import json
import copy
import logging


def read_all_json_files(label_dir, ply_dir):
    logging.info(f"Reading JSON files from directory: {label_dir}")
    file_list = os.listdir(label_dir)
    file_list.sort()
    data_list = []

    for file in file_list:
        if file == '_classes.json':
            logging.info("Skipping '_classes.json'")
            continue
        
        file_path = os.path.join(label_dir, file)
        
        if not os.path.exists(file_path):
            logging.warning("File does not exist: %s", file_path)
            continue
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                logging.info(f"Loaded JSON data from: {file_path}")

            # Modify the folder that contains the ply file
            data['folder'] =  os.path.normpath(ply_dir)
            logging.debug(f"Updated folder path in JSON data to: {ply_dir}")

            # Modify the label path
            path = data['path']
            if len(data['objects']) == 0:
                logging.warning(f"Removing empty file: {file_path}")
                os.remove(file_path)
                continue
            
            # Get the filename without parents directory
            path = path.split('/')[-1]
            path = os.path.join(os.getcwd(), ply_dir, path)
            data['path'] =  os.path.normpath(path)
            logging.debug(f"Updated path in JSON data to: {path}")

            # Write to JSON file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
                logging.info(f"Saved updated JSON data to: {file_path}")

        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
            


class DataPreprocessor(QThread):
    progress = pyqtSignal(str)

    def __init__(self, input_dir, label_dir, k_points, nb_neighbors, std_ratio, roi_range):
        super().__init__()
        self.input_data_dir = input_dir
        self.parent_dir = os.path.dirname(input_dir)  # Get the parent directory
        self.modified_data_dir = os.path.join(self.parent_dir, "modified_data")
        self.label_dir = label_dir
        self.modified_label_dir = os.path.join(self.parent_dir, "modified_labels")
        self._is_running = True  # Control flag for thread cancellation
        
        self.k_points = k_points
        self.nb_neighbors = nb_neighbors
        self.std_ratio = std_ratio
        self.roi_range = roi_range
        
        # Check if the directories exist and delete their contents if they do
        if os.path.exists(self.modified_data_dir):
            shutil.rmtree(self.modified_data_dir)  # Delete the directory and its contents
            logging.info(f'{self.modified_data_dir} already exist, recreating new folder....')
            self.progress.emit(f'{self.modified_data_dir} already exist, recreating new folder....')
        if os.path.exists(self.modified_label_dir):
            shutil.rmtree(self.modified_label_dir)  # Delete the directory and its contents
            logging.info(f'{self.modified_label_dir} already exist, recreating new folder....')
            self.progress.emit(f'{self.modified_label_dir} already exist, recreating new folder....')
    
        # Create directories
        os.makedirs(self.modified_data_dir, exist_ok=True)
        os.makedirs(self.modified_label_dir, exist_ok=True)

        logging.info("DataPreprocessor initialized with input_dir: %s, label_dir: %s", input_dir, label_dir)

    def run(self):
        file_names = os.listdir(self.input_data_dir)

        if not os.listdir(self.modified_data_dir):  # Check if the directory is empty
            for idx, file_name in enumerate(file_names):
                if not file_name.endswith('.ply'):
                    logging.warning("Skipping non-Ply file: %s", file_name)
                    self.progress.emit(f"Skipping non-Ply file: {file_name}")
                    continue

                if not self._is_running:
                    self.progress.emit("Preprocessing cancelled.")
                    logging.info("Preprocessing cancelled by user.")
                    return

                self.progress.emit(f'Processing {file_name}...')
                logging.info("Processing file: %s", file_name)
                file_path = os.path.join(self.input_data_dir, file_name)

                try:
                    filtered_pcd = self.downsample_and_remove_outliers(file_path,  self.k_points, self.nb_neighbors, self.std_ratio)
                    if filtered_pcd is None:
                        self.progress.emit(f"Filtered point cloud for {file_name} is empty.")
                        logging.warning("Filtered point cloud for %s is empty.", file_name)
                        continue

                    self.split_points(file_name, filtered_pcd, idx, file_names, self.roi_range)
                    self.progress.emit(f'{file_name} processed ({idx + 1}/{len(file_names)})')
                    logging.info("File %s processed successfully.", file_name)

                except Exception as e:
                    self.progress.emit(f"Error processing {file_name}: {str(e)}")
                    logging.error("Error processing file %s: %s", file_name, str(e))
             
            # fix the path of the labels
            read_all_json_files(self.modified_label_dir, self.modified_data_dir)   
            
            self.progress.emit('Data preprocessing completed!')
            
            self.progress.emit(f"Preprocessed data save to {self.modified_data_dir}")
            self.progress.emit(f"Preprocessed label save to {self.modified_label_dir}")
            logging.info("Data preprocessing completed!")
        else:
            self.progress.emit(f"The directory '{self.modified_data_dir}' is not empty")
            logging.warning("The directory '%s' is not empty", self.modified_data_dir)

    def downsample_and_remove_outliers(self, file_path, k_points, nb_neighbors, std_ratio):
        """Downsample the point cloud and remove outliers."""
        try:
            pcd = o3d.io.read_point_cloud(file_path)
            logging.info("Loaded point cloud from %s", file_path)
        except Exception as e:
            logging.error("Error loading point cloud from %s: %s", file_path, str(e))
            return None

        # Downsampling
        uni_down_pcd = pcd.uniform_down_sample(every_k_points=k_points)
        logging.info("Downsampled point cloud from %s", file_path)

        # Outlier removal
        cl, ind = uni_down_pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
        logging.info("Removed outliers from point cloud")

        inlier_cloud = uni_down_pcd.select_by_index(ind)  # Filter out inliers
        inlier_cloud_np = np.array(inlier_cloud.points)

        if inlier_cloud_np.size == 0:
            logging.warning("No inliers found in %s.", file_path)
            return None  # Return None if no points

        filtered_pcd = o3d.geometry.PointCloud()
        filtered_pcd.points = o3d.utility.Vector3dVector(inlier_cloud_np)

        return filtered_pcd
        
    def split_points(self, file_name, filtered_pcd, idx, file_names, roi_range):
        """Split the filtered point cloud into two parts and save them."""
        save_path_1 = os.path.join(self.modified_data_dir, file_name.replace(".ply", "_part1.ply"))
        save_path_2 = os.path.join(self.modified_data_dir, file_name.replace(".ply", "_part2.ply"))
        save_paths = [save_path_1, save_path_2]

        inlier_cloud_np = np.array(filtered_pcd.points)

        x_range = roi_range  # Fixed ROI
        x_mid_thresh = x_range / 2
        x_min_thresh = 0.23
        x_max_thresh = 0.77

        part_1 = inlier_cloud_np[np.where(inlier_cloud_np[:, 0] > x_mid_thresh)]
        part_1 = part_1[np.where(part_1[:, 0] < x_max_thresh * x_range)]
        part_1[:, 0] = part_1[:, 0] - x_mid_thresh

        part_2 = inlier_cloud_np[np.where(inlier_cloud_np[:, 0] <= x_mid_thresh)]
        part_2 = part_2[np.where(part_2[:, 0] > x_min_thresh * x_range)]
        part_2[:, 0] = part_2[:, 0] - x_min_thresh * x_range

        inlier_cloud_nps = [part_1, part_2]

        for inlier_cloud_np, save_path in zip(inlier_cloud_nps, save_paths):
            splitted_pcd = o3d.geometry.PointCloud()
            splitted_pcd.points = o3d.utility.Vector3dVector(inlier_cloud_np)
            o3d.io.write_point_cloud(save_path, splitted_pcd)
            logging.info("Saved split point cloud to %s", save_path)

        self.modify_labels(file_name, idx, file_names, x_mid_thresh, x_range)

    def modify_labels(self, file_name, idx, file_names, x_mid_thresh, x_range):
        """Modify the original label files based on the split point clouds."""
        try:
            ori_label_path = os.path.join(self.label_dir, file_name.replace(".ply", ".json"))
            if not os.path.exists(ori_label_path):
                self.progress.emit(f"Original label file not found for {file_name}.")
                logging.warning("Original label file not found for %s.", file_name)
                return
            
            label_path_1 = os.path.join(self.modified_label_dir, file_name.replace(".ply", "_part1.json"))
            label_path_2 = os.path.join(self.modified_label_dir, file_name.replace(".ply", "_part2.json"))
            label_paths = [label_path_1, label_path_2]

            with open(ori_label_path) as f:
                data = json.load(f)
                logging.info("Loaded original label file from %s", ori_label_path)

            objs = data['objects']
            objs_part_1 = []
            objs_part_2 = []
            for obj in objs:
                if obj['centroid']['x'] > x_mid_thresh:
                    obj['centroid']['x'] -= x_mid_thresh
                    objs_part_1.append(obj)
                else:
                    obj['centroid']['x'] -= (0.23 * x_range)
                    objs_part_2.append(obj)

            splitted_objs = [objs_part_1, objs_part_2]

            for i, (label_path, objs) in enumerate(zip(label_paths, splitted_objs)):
                new_data = copy.deepcopy(data)
                new_data['objects'] = objs
                new_data['filename'] = new_data['filename'].replace(".ply", f"_part{i + 1}.ply")
                new_data['path'] = new_data['path'].replace(".ply", f"_part{i + 1}.ply")

                with open(label_path, 'w') as f:
                    json.dump(new_data, f, indent=4)
                    logging.info("Saved modified label file to %s", label_path)

        except Exception as e:
            logging.error("Error modifying labels: %s", str(e))
            


                
    def stop(self):
        self._is_running = False
        logging.info("Preprocessing stopped by user.")
