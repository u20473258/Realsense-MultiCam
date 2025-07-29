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
#include <thread>
#include <utility>
#include <vector>


// Saves metadata to a text file
void metadata_to_text(const rs2::frame& frm, const std::string& file_name)
{
    // Create and open text file for the metadata
    std::ofstream text_metadata_file;
    text_metadata_file.open(file_name);

    text_metadata_file << "Stream," << rs2_stream_to_string(frm.get_profile().stream_type()) << "\nMetadata Attribute,Value\n";

    // Record all the available metadata attributes
    for (size_t i = 0; i < RS2_FRAME_METADATA_COUNT; i++)
    {
        if (frm.supports_frame_metadata((rs2_frame_metadata_value)i))
        {
            text_metadata_file << rs2_frame_metadata_to_string((rs2_frame_metadata_value)i) << ","
                << frm.get_frame_metadata((rs2_frame_metadata_value)i) << "\n";
        }
    }

    text_metadata_file.close();
}


void save_frame_depth_data(const std::string& pi_name, rs2::frame frame)
{
    // Create filters
    rs2::decimation_filter dec_filter;
    rs2::spatial_filter spat_filter;
    rs2::disparity_transform depth_to_disparity(true);
    rs2::disparity_transform disparity_to_depth(false);

    // Configure filters
    dec_filter.set_option(RS2_OPTION_FILTER_MAGNITUDE, 3);
    spat_filter.set_option(RS2_OPTION_FILTER_SMOOTH_ALPHA, 0.6f); // Delta is 20 by default

    // Filter depth frame
    frame = dec_filter.process(frame);
    frame = depth_to_disparity.process(frame);
    frame = spat_filter.process(frame);
    frame = disparity_to_depth.process(frame);

    // We can only save video frames, so we skip the rest
    if (auto image = frame.as<rs2::video_frame>())
    {
        // Create file name
        std::stringstream file_name;
        file_name << "depth/" << pi_name << "_depth_" << frame.get_frame_number() << ".raw";

        std::ofstream outfile(file_name.str(), std::ofstream::binary);
        outfile.write(static_cast<const char*>(image.get_data()), image.get_width() * image.get_height() * image.get_bytes_per_pixel());

        std::cout << "Saved " << file_name.str() << std::endl;
        outfile.close();

        // Create metadata file name
        std::stringstream text_metadata_file;
        text_metadata_file << "depth_metadata/" << pi_name << "_depth_metadata_" << image.get_frame_number() << ".txt";

        // Record per-frame metadata for UVC streams
        metadata_to_text(image, text_metadata_file.str());
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
        std::stringstream text_metadata_file;
        text_metadata_file << "colour_metadata/" << pi_name << "_colour_metadata_" << frame.get_frame_number() << ".txt";

        // Record per-frame metadata for UVC streams
        metadata_to_text(image, text_metadata_file.str());
    }

}

// Capture depth and color video streams and store them in specific files
int main(int argc, char * argv[]) try
{
    // Check for connected realsense camera
    rs2::context ctx;
    auto devices = ctx.query_devices();

    if (devices.size() == 0) {
        std::cerr << "No RealSense devices found!" << std::endl;
        return EXIT_FAILURE;
    }

    // Congifure the streaming configurations
    rs2::config cfg;
    cfg.enable_stream(RS2_STREAM_DEPTH, 1280, 720, RS2_FORMAT_Z16, 15);
    cfg.enable_stream(RS2_STREAM_COLOR, 424, 240, RS2_FORMAT_RGB8, 15);

    // Create pipe and start it
    rs2::pipeline pipe;
    pipe.start(cfg);

    // Get the number of frames from user
    char *output;
    auto num_frames = strtol(argv[1], &output, 10);

    // Store the raspberry pi name for file name purposes
    std::string raspi_name = argv[2];

    // Capture 30 frames to give autoexposure, etc. a chance to settle
    for (auto i = 0; i < 30; ++i) pipe.wait_for_frames();

    // Create a vector to store threads
    std::vector<std::thread> threads;
    for (auto i = 0; i < num_frames; ++i)
    {
        rs2::frameset data = pipe.wait_for_frames();

        // Create a thread for each frame and process it in parallel
        threads.emplace_back(save_frame_depth_data, raspi_name, data.get_depth_frame());
        threads.emplace_back(save_frame_color_data, raspi_name, data.get_color_frame());
    }

    // Ensure all threads are done before terminating program
    for (auto &t : threads)
    {
        if (t.joinable())
            t.join();
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


