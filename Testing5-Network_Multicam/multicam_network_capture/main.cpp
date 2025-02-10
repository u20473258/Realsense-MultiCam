// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2017 Intel Corporation. All Rights Reserved.

#include <librealsense2/rs.hpp> // Include RealSense Cross Platform API
#include <librealsense2-net/rs_net.hpp>

// 3rd party header for writing png files
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <map>
#include <vector>


void metadata_to_csv(const rs2::frame& frm, const std::string& filename)
{
    std::ofstream csv;

    csv.open(filename);

    csv << "Stream," << rs2_stream_to_string(frm.get_profile().stream_type()) << "\nMetadata Attribute,Value\n";

    // Record all the available metadata attributes
    for (size_t i = 0; i < RS2_FRAME_METADATA_COUNT; i++)
    {
        if (frm.supports_frame_metadata((rs2_frame_metadata_value)i))
        {
            csv << rs2_frame_metadata_to_string((rs2_frame_metadata_value)i) << ","
                << frm.get_frame_metadata((rs2_frame_metadata_value)i) << "\n";
        }
    }

    csv.close();
}

void save_frame_depth_data(const std::string& serial_number, rs2::frame frame)
{
    rs2::depth_frame depth = frame.as<rs2::depth_frame>();
    if (auto image = frame.as<rs2::video_frame>())
    {
        std::ofstream myfile;
        std::stringstream filename;
        filename << "camera_" << serial_number << "/depth/" << frame.get_frame_number() << ".csv";
        myfile.open(filename.str());
        myfile << std::setprecision(2);

        for (auto y = 0; y < image.get_height(); y++)
        {
            for (auto x = 0; x < image.get_width(); x++)
            {
                myfile << depth.get_distance(x, y) << ", ";
            }
            myfile << "\n";
        }
        std::cout << "Saved " << filename.str() << std::endl;
        myfile.close();
        
        // Record per-frame metadata for UVC streams
        std::stringstream csv_file;
        csv_file << "camera_" << serial_number << "/depth_metadata/" << frame.get_frame_number() << ".csv";
        metadata_to_csv(image, csv_file.str());
    }
}

void save_frame_color_data(const std::string& serial_number, rs2::frame frame)
{
    // We can only save video frames as pngs, so we skip the rest
    if (auto image = frame.as<rs2::video_frame>())
    {
        // Write images to disk
        std::stringstream png_file;
        png_file << "camera_" << serial_number << "/colour/" << frame.get_frame_number() << ".png";
        stbi_write_png(png_file.str().c_str(), image.get_width(), image.get_height(),
                       image.get_bytes_per_pixel(), image.get_data(), image.get_stride_in_bytes());
        std::cout << "Saved " << png_file.str() << std::endl;

        // Record per-frame metadata for UVC streams
        std::stringstream csv_file;
        csv_file << "camera_" << serial_number << "/colour_metadata/" << frame.get_frame_number() << ".csv";
        metadata_to_csv(image, csv_file.str());
    }

}

// Capture Example demonstrates how to
// capture depth and color video streams and render them to the screen
int main(int argc, char * argv[]) try
{
    // Create librealsense context for managing devices
    rs2::context ctx;

    // Create network devices and add them to the context
    rs2::net_device raspi1("192.168.249.151"); raspi1.add_to(ctx);
    rs2::net_device raspi2("192.168.249.150"); raspi2.add_to(ctx);

    // Declare map from device serial number to colorizer (utility class to convert depth data RGB colorspace)
    std::map<std::string, rs2::colorizer> colorizers;

    // Create pipelines for the cameras
    std::vector<rs2::pipeline> pipelines;

    // Capture serial numbers before opening streaming
    std::vector<std::string> serials = {"138322250306", "141322252882"};
    int num_cameras = 2;

    // Start a streaming pipe per each connected device
    for (auto&& serial : serials)
    {
        rs2::pipeline pipe(ctx);
        rs2::config cfg;
        cfg.enable_device(serial);
        cfg.enable_stream(RS2_STREAM_DEPTH, 640, 480, RS2_FORMAT_Z16, 30);
        cfg.enable_stream(RS2_STREAM_COLOR, 640, 480, RS2_FORMAT_RGB8 , 30);
        pipe.start(cfg);
        pipelines.emplace_back(pipe);
        // Map from each device's serial number to a different colorizer
        colorizers[serial] = rs2::colorizer();
    }
    
    // Main app loop
    while (true) {
        rs2::frame depth, color;

        // Collect and save the new frames from all the connected devices
        for (int i = 0; i < num_cameras; i++) {
            // Wait for next set of frames from the camera
            rs2::frameset data = pipelines[i].wait_for_frames();

            // Find the depth data
            depth = data.get_depth_frame();

            // Find the color data
            color = data.get_color_frame();

            // Save the data
            save_frame_depth_data(serials[i], depth);
            save_frame_color_data(serials[i], color);
        }
    }

    return EXIT_SUCCESS;
}
catch (const rs2::error & e)
{
    std::cerr << "RealSense error calling " << e.get_failed_function() << "(" << e.get_failed_args() << "):\n    " << e.what() << std::endl;
    return EXIT_FAILURE;
}
catch (const std::exception& e)
{
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
}
