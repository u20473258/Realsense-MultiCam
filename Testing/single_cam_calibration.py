import cv2
import numpy as np
import glob

# Parameters
chessboard_size = (4, 5)  # Number of inner corners per row and column (adjust based on your chessboard)
square_size = 0.053       # Square size in meters (adjust based on your chessboard)

# Prepare object points (3D points in real-world space)
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size  # Scale the points to the actual square size

# Arrays to store object points and image points from all images
objpoints = []       # 3D points in real-world space
imgpoints = []       # 2D points in image plane

# Load images
images = glob.glob('cam2_calibration/*.png')  # Path to your chessboard images

# Process each image
for image_path in images:
    # Load image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Find chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
    
    # If found, add object points, image points (after refining them)
    if ret:
        corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                           criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        objpoints.append(objp)
        imgpoints.append(corners_refined)
        
        # Draw and display the corners
        cv2.drawChessboardCorners(img, chessboard_size, corners_refined, ret)
        cv2.imshow('Chessboard', img)
        cv2.waitKey(500)  # Display each image for 500ms
    else:
        print(f"Chessboard not found in image: {image_path}")

cv2.destroyAllWindows()

# Perform camera calibration
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

# Print the results
print("Camera matrix:")
print(camera_matrix)
print("\nDistortion coefficients:")
print(dist_coeffs)

# Save the results for future use
np.save("camera_matrix.npy", camera_matrix)
np.save("distortion_coefficients.npy", dist_coeffs)

print("Calibration complete. Parameters saved to files.")
