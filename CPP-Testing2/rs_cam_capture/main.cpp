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


void metadata_to_csv(const rs2::frame& frm, const std::string& filename)
{
    std::ofstream csv;

    csv.open(filename);

    //    std::cout << "Writing metadata to " << filename << endl;
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

void save_frame_depth_data(const std::string& filename,
                           rs2::frame frame)
{
    rs2::depth_frame depth = frame.as<rs2::depth_frame>();
    if (auto image = frame.as<rs2::video_frame>())
    {
        std::ofstream myfile;
        std::stringstream fullname;
        fullname << filename << "_" << frame.get_frame_number() << ".csv";
        myfile.open(fullname.str());
        myfile << std::setprecision(2);

        for (auto y = 0; y < image.get_height(); y++)
        {
            for (auto x = 0; x < image.get_width(); x++)
            {
                myfile << depth.get_distance(x, y) << ", ";
            }
            myfile << "\n";
        }
        std::cout << "Saved " << fullname.str() << std::endl;
        myfile.close();
        
        // Record per-frame metadata for UVC streams
        std::stringstream csv_file;
        csv_file << image.get_profile().stream_name()
                 << "_" << frame.get_frame_number()
                 << "_metadata.csv";
        metadata_to_csv(image, csv_file.str());
    }
}

void save_frame_color_data(const std::string& filename,
                           rs2::frame frame)
{
    // We can only save video frames as pngs, so we skip the rest
    if (auto image = frame.as<rs2::video_frame>())
    {
        // Write images to disk
        std::stringstream png_file;
        png_file << image.get_profile().stream_name() << "_" << frame.get_frame_number() << ".png";
        stbi_write_png(png_file.str().c_str(), image.get_width(), image.get_height(),
                       image.get_bytes_per_pixel(), image.get_data(), image.get_stride_in_bytes());
        std::cout << "Saved " << png_file.str() << std::endl;

        // Record per-frame metadata for UVC streams
        std::stringstream csv_file;
        csv_file << image.get_profile().stream_name()
                 << "_" << frame.get_frame_number()
                 << "_metadata.csv";
        metadata_to_csv(image, csv_file.str());
    }

}

// Capture Example demonstrates how to
// capture depth and color video streams and render them to the screen
int main(int argc, char * argv[]) try
{
    rs2::colorizer color_map;

    rs2::pipeline pipe;
    pipe.start();

    // Capture 30 frames to give autoexposure, etc. a chance to settle
    for (auto i = 0; i < 30; ++i) pipe.wait_for_frames();

    while(true) // Application still alive?
    {
        rs2::frameset data = pipe.wait_for_frames(); // Wait for next set of frames from the camera

        rs2::frame depth = data.get_depth_frame(); // Find the depth data
        rs2::frame color = data.get_color_frame(); // Find the color data

        save_frame_depth_data("depth", depth);
        save_frame_color_data("color", color);
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


