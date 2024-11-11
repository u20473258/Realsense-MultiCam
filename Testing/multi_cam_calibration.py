import cv2
import numpy as np
import glob

# Parameters
chessboard_size = (4, 5)  # Number of inner corners per row and column
square_size = 0.053       # Square size in meters (adjust based on your chessboard)

# Prepare object points (3D points in real-world space)
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size  # Scale the points to the actual square size

# Arrays to store object points and image points from both cameras
objpoints = []        # 3D points in real world space
imgpoints_left = []   # 2D points in left camera image plane
imgpoints_right = []  # 2D points in right camera image plane

# Load images
left_images = sorted(glob.glob('cam1_calibration/*.png'))   # Path to left camera images
right_images = sorted(glob.glob('cam2_calibration/*.png')) # Path to right camera images

# Check that each left image has a corresponding right image
if len(left_images) != len(right_images):
    raise ValueError("Number of left and right images must be the same")

# Process each pair of images
for left_img_path, right_img_path in zip(left_images, right_images):
    # Load images
    img_left = cv2.imread(left_img_path)
    img_right = cv2.imread(right_img_path)
    
    # Convert to grayscale
    gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)
    
    # Find chessboard corners
    ret_left, corners_left = cv2.findChessboardCorners(gray_left, chessboard_size, None)
    ret_right, corners_right = cv2.findChessboardCorners(gray_right, chessboard_size, None)
    
    if ret_left and ret_right:
        # Refine corner positions for more accurate calibration
        corners_left = cv2.cornerSubPix(gray_left, corners_left, (11, 11), (-1, -1),
                                        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        corners_right = cv2.cornerSubPix(gray_right, corners_right, (11, 11), (-1, -1),
                                         criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        
        # Store object points and image points for each camera
        objpoints.append(objp)
        imgpoints_left.append(corners_left)
        imgpoints_right.append(corners_right)
        
        # Optionally, draw and display the corners to check alignment
        cv2.drawChessboardCorners(img_left, chessboard_size, corners_left, ret_left)
        cv2.drawChessboardCorners(img_right, chessboard_size, corners_right, ret_right)
        cv2.imshow('Left Camera', img_left)
        cv2.imshow('Right Camera', img_right)
        cv2.waitKey(500)  # Wait 500ms to see the image (press any key to skip)
    else:
        print(f"Chessboard not found in image pair: {left_img_path}, {right_img_path}")

cv2.destroyAllWindows()

# Intrinsic parameters (example values - replace with actual intrinsic parameters if known)
# Assuming the cameras are calibrated; otherwise, calibrate individually using cv2.calibrateCamera
cameraMatrix1 = np.array([[393.91834631, .0, 318.38931192], [0, 384.54044476, 218.19374103], [0, 0, 1]])  # Left camera matrix
distCoeffs1 = np.array([[-0.05293681, 0.0971027, -0.01973799, -0.01271367, -0.06797392]]) 
cameraMatrix2 = np.array([[392.50936185, 0.0, 312.31082791], [0, 390.92602104, 239.27569162], [0, 0, 1]])  # Right camera matrix
distCoeffs2 = np.array([[-0.06650369, 0.03260221, -0.01042748, -0.00454311, 0.27933907]])

print(gray_left.shape[::-1])

# Stereo calibration to find the rotation and translation between the two cameras
# R = None
# T = None
# E = None
# F = None
retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(
    objpoints, imgpoints_left, imgpoints_right,
    cameraMatrix1, distCoeffs1,
    cameraMatrix2, distCoeffs2,
    gray_left.shape[::-1],  # Image size (width, height)
    flags=cv2.CALIB_FIX_INTRINSIC,
    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
)

# Print extrinsic parameters
print("Rotation matrix (R):")
print(R)
print("Translation vector (T):")
print(T)

# Save the results for later use
np.save("extrinsics_rotation.npy", R)
np.save("extrinsics_translation.npy", T)

print("Extrinsic calibration complete. Parameters saved to files.")
