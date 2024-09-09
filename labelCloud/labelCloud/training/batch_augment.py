import open3d as o3d
import numpy as np
import os, json
from math import cos, sin
from tqdm import tqdm


'''
# reference
http://www.open3d.org/docs/release/python_example/io/index.html
http://www.open3d.org/docs/release/tutorial/geometry/pointcloud.html#Paint-point-cloud
http://www.open3d.org/docs/latest/tutorial/Advanced/multiway_registration.html
http://www.open3d.org/docs/0.9.0/tutorial/Basic/working_with_numpy.html
'''

################################
# Check if a point in bbox or not
################################
def check_point_within_bbox(point, x_centroid, y_centroid, z_centroid,
                                length, width, height, rotation):

    # Calculate half-dimensions for convenience
    half_length = length / 2
    half_width = width / 2
    half_height = height / 2
    
    # Create rotation matrix
    rotation_matrix = np.array([[np.cos(rotation), -np.sin(rotation), 0],
                                [np.sin(rotation), np.cos(rotation), 0],
                                [0, 0, 1]])
    
    # Calculate inverse rotation matrix
    inverse_rotation_matrix = np.array([[np.cos(-rotation), -np.sin(-rotation), 0],
                                        [np.sin(-rotation), np.cos(-rotation), 0],
                                        [0, 0, 1]])
    
    # Translate the point relative to the bbox's centroid
    translated_point = point - np.array([x_centroid, y_centroid, z_centroid])
    
    # Apply inverse rotation to the translated point
    aligned_point = np.dot(translated_point, inverse_rotation_matrix.T)
    
    # Check if the aligned point is within the bbox
    is_within_bbox = (
        np.abs(aligned_point[0]) <= half_length and
        np.abs(aligned_point[1]) <= half_width and
        np.abs(aligned_point[2]) <= half_height
    )
    
    #print("Point is within bbox:", is_within_bbox)
    return is_within_bbox

################################
# Augment
################################
def rotate_point(point, rot_angle_z, rot_origin_x, rot_origin_y):
    # extract xyz of point to be rotated
    x = point[0]
    y = point[1]
    z = point[2]
    new_x = np.cos(rot_angle_z) * (x - rot_origin_x) - np.sin(rot_angle_z) * (y - rot_origin_y) + rot_origin_x
    new_y = np.sin(rot_angle_z) * (x - rot_origin_x) + np.cos(rot_angle_z) * (y - rot_origin_y) + rot_origin_y
    new_point = np.array([new_x, new_y, z])
    return new_point
    
def augment(np_pcd, obj, aug_type=None):
    '''
    all augmentation type
    -1: no augment
    0: remove obj
    1: move upward
    2: top/down flip
    3: rotate left/right

    augmentation is performed at two sections (refer AUGMENT SECTION header below)
    '''
    # no augment
    if aug_type == -1:
        return np_pcd, obj
    elif aug_type == 0:
        pass
    elif aug_type == 1:
        displacement = np.random.uniform(0.2, 0.4, 1)[0]
    elif aug_type == 2:
        pass
    elif aug_type == 3:
        rot_angle_z = np.random.uniform(0.4, 1.5, 1)[0] # radian
        if np.random.rand() > 0.5:
            rot_angle_z *= -1

    # extract bbox properties
    x_centroid = obj['centroid']['x']
    y_centroid = obj['centroid']['y']
    z_centroid = obj['centroid']['z']
    length = obj['dimensions']['length']
    width = obj['dimensions']['width']
    height = obj['dimensions']['height']
    rotation = obj['rotations']['z']

    selected_points = []
    selected_indexs = []

    ave_x, ave_y = [], [] # to calculate new centroid (for type 3: rotate left/right)
    for i in range(len(np_pcd)):
        point = np_pcd[i]
        is_within_bbox = check_point_within_bbox(point, x_centroid, y_centroid, z_centroid,
                                                    length, width, height, rotation)
        # if the point is in the bbox
        if is_within_bbox:
            selected_points.append(point)
            selected_indexs.append(i)
            
            ######################
            # AUGMENT SECTION 1
            ######################
            # 0: if delete
            if aug_type == 0: 
                # no augmentation required here, just have to delete the points in Section 2
                pass
                
            # 1: if move upward
            elif aug_type == 1: 
                new_point = point + np.array([0, 0, displacement])
                np_pcd[i] = new_point    
            
            # 2: if top/down flip
            elif aug_type == 2:
                # no augmentation required here, do in Section 2
                pass
            
            # 3: rotate left/right (< y mid)
            # find the origin for rotation
            elif aug_type == 3:
                if y_centroid < y_mid:
                    # dunno how to explain but yup, we need two part
                    rot_origin_x = x_centroid
                    rot_origin_y = (y_centroid + width / 2)
                    origin_1 = rotate_point([rot_origin_x, rot_origin_y, -1], -1 * (3.14159265 - rotation), x_centroid, y_centroid)
                    x1, y1 = origin_1[0], origin_1[1]

                    # dunno how to explain but yup, we need two part
                    rot_origin_x = x_centroid
                    rot_origin_y = (y_centroid - width / 2)
                    origin_2 = rotate_point([rot_origin_x, rot_origin_y, -1], -1 * (3.14159265 - rotation), x_centroid, y_centroid)
                    x2, y2 = origin_2[0], origin_2[1]

                    if y1 < y2:
                        rot_origin_x = x1
                        rot_origin_y = y1
                    else:
                        rot_origin_x = x2
                        rot_origin_y = y2

                else:
                    # dunno how to explain but yup, we need two part
                    rot_origin_x = x_centroid
                    rot_origin_y = (y_centroid + width / 2)
                    origin_1 = rotate_point([rot_origin_x, rot_origin_y, -1], -1 * (3.14159265 - rotation), x_centroid, y_centroid)
                    x1, y1 = origin_1[0], origin_1[1]

                    # dunno how to explain but yup, we need two part
                    rot_origin_x = x_centroid
                    rot_origin_y = (y_centroid - width / 2)
                    origin_2 = rotate_point([rot_origin_x, rot_origin_y, -1], -1 * (3.14159265 - rotation), x_centroid, y_centroid)
                    x2, y2 = origin_2[0], origin_2[1]

                    if y1 > y2:
                        rot_origin_x = x1
                        rot_origin_y = y1
                    else:
                        rot_origin_x = x2
                        rot_origin_y = y2

                # rotation angle at z            
                rot_angle_z = rot_angle_z

                # edit the point
                new_point = rotate_point(point, rot_angle_z, rot_origin_x, rot_origin_y)
                np_pcd[i] = new_point
                
                # update ave_x, ave_y to calculate new centroid
                ave_x.append(new_point[0])
                ave_y.append(new_point[1])


    ######################
    # AUGMENT SECTION 2
    ###################### 
    # 0: if delete
    if aug_type == 0:
        # augment ply
        np_pcd = np.delete(np_pcd, selected_indexs, axis=0)
        
        # augment label
        obj = None

    # 1: if move upward    
    elif aug_type == 1:   
        # augment label
        obj['centroid']['z'] = obj['centroid']['z'] + displacement

    # 2: if top/down flip
    elif aug_type == 2: 
        # augment ply
        selected_points = np.array(selected_points) 
        z_plane = z_min = np.min(selected_points[:, 2]) 
        z_coords = selected_points[:, 2]
        z_coords = z_coords - z_plane # bring down the object to z=0 plane
        z_coords = -1 * z_coords # flip the opject at z=0
        z_coords = z_coords * 0.5 # squeeze in z dimension
        z_coords = z_coords + z_plane # bring back up
        selected_points[:, 2] = z_coords 
        np_pcd[selected_indexs] = selected_points
        
        # augmetn label similarly
        obj['centroid']['z'] = (-1 * (z_centroid - z_plane)) * 0.5 + z_plane
        obj['dimensions']['height'] = obj['dimensions']['height'] * 0.5
    
    # 3: rotate left/right
    elif aug_type == 3:
        # augment label
        x_centroid = sum(ave_x) / len(ave_x)
        y_centroid = sum(ave_y) / len(ave_y)
        rotation = rotation + rot_angle_z
        
        obj['centroid']['x'] = x_centroid
        obj['centroid']['y'] = y_centroid
        obj['rotations']['z'] = rotation      

    if obj is not None: obj['name'] = 'defect'

    return np_pcd, obj
