// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2017 Intel Corporation. All Rights Reserved.

#include <librealsense2/rs.hpp> // Include RealSense Cross Platform API

// 3rd party header for writing png files
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>


void metadata_to_csv(const rs2::frame& frm, const std::string& file_name)
{
    // Create and open csv file for the metadata
    std::ofstream csv_metadata_file;
    csv_metadata_file.open(file_name);

    csv_metadata_file << "Stream," << rs2_stream_to_string(frm.get_profile().stream_type()) << "\nMetadata Attribute,Value\n";

    // Record all the available metadata attributes
    for (size_t i = 0; i < RS2_FRAME_METADATA_COUNT; i++)
    {
        if (frm.supports_frame_metadata((rs2_frame_metadata_value)i))
        {
            csv_metadata_file << rs2_frame_metadata_to_string((rs2_frame_metadata_value)i) << ","
                << frm.get_frame_metadata((rs2_frame_metadata_value)i) << "\n";
        }
    }

    csv_metadata_file.close();
}

void save_frame_depth_data(const std::string& pi_name, rs2::frame frame)
{
    // Get the depth frame from the given frame
    rs2::depth_frame depth = frame.as<rs2::depth_frame>();

    // We can only save video frames as csvs, so we skip the rest
    if (auto image = frame.as<rs2::video_frame>())
    {
        // Create csv file name
        std::stringstream file_name;
        file_name << "depth/" << pi_name << "_depth_" << frame.get_frame_number() << ".csv";

        // Create csv file
        std::ofstream csv_depth_file;
        csv_depth_file.open(file_name.str());
        csv_depth_file << std::setprecision(2);
        
        // Get the depth at each pixel index and store it in the csv
        for (auto y = 0; y < image.get_height(); y++)
        {
            for (auto x = 0; x < image.get_width(); x++)
            {
                csv_depth_file << depth.get_distance(x, y) << ", ";
            }
            csv_depth_file << "\n";
        }
        std::cout << "Saved " << file_name.str() << std::endl;
        csv_depth_file.close();

        // Create metadata file name
        std::stringstream csv_metadata_file;
        csv_metadata_file << "depth_metadata/" << pi_name << "_depth_metadata_" << frame.get_frame_number() << ".csv";

        // Record per-frame metadata for UVC streams
        metadata_to_csv(image, csv_metadata_file.str());
    }
}

void save_frame_color_data(const std::string& pi_name, rs2::frame frame)
{
    // We can only save video frames as pngs, so we skip the rest
    if (auto image = frame.as<rs2::video_frame>())
    {
        // Create the file name
        std::stringstream png_colour_file;
        png_colour_file << "colour/" << pi_name << "_colour_" << frame.get_frame_number() << ".png";

        // Convert colour frame to a png and save it
        stbi_write_png(png_colour_file.str().c_str(), image.get_width(), image.get_height(),
                       image.get_bytes_per_pixel(), image.get_data(), image.get_stride_in_bytes());
        std::cout << "Saved " << png_colour_file.str() << std::endl;

        // Create metadata file name
        std::stringstream csv_metadata_file;
        csv_metadata_file << "colour_metadata/" << pi_name << "_colour_metadata_" << frame.get_frame_number() << ".csv";

        // Record per-frame metadata for UVC streams
        metadata_to_csv(image, csv_metadata_file.str());
    }

}

// Capture depth and color video streams and store them in specific files
int main(int argc, char * argv[]) try
{
    // Congifure the streaming configurations
    rs2::config cfg;
    cfg.enable_stream(RS2_STREAM_DEPTH, 640, 480, RS2_FORMAT_Z16, 15);
    cfg.enable_stream(RS2_STREAM_COLOR, 640, 480, RS2_FORMAT_RGB8, 15);

    // Create pipe and start it
    rs2::pipeline pipe;
    pipe.start(cfg);

    // Get the number of frames from user
    char *output;
    auto num_frames = strtol(argv[1], &output, 10);

    // Store the raspberry pi name for file name purposes
    std::string raspi_name = "raspi1";

    // Capture 30 frames to give autoexposure, etc. a chance to settle
    for (auto i = 0; i < 30; ++i) pipe.wait_for_frames();

    // Capture num_frames frames
    for (auto i = 0; i < num_frames; ++i)
    {
        // Wait for next set of frames
        rs2::frameset data = pipe.wait_for_frames();

        // Get depth and colour frame
        rs2::frame depth = data.get_depth_frame();
        rs2::frame color = data.get_color_frame();

        // Save depth and colour frames
        save_frame_depth_data(raspi_name, depth);
        save_frame_color_data(raspi_name, color);
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


