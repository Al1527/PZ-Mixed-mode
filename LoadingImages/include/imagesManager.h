#pragma once

#include "opencv2/core/cvstd.hpp"
#include "opencv2/core/types.hpp"
#include <opencv2/opencv.hpp>
#include <vector>
#include <filesystem>

void putImagesToDirectory(std::filesystem::path directoryPath, std::vector<cv::Mat> images);
void putImageToDirectory(std::filesystem::path directoryPath, cv::Mat image, std::string name);
void loadImages(std::filesystem::path directoryPath, std::vector<cv::Mat> &images);
void showImage(cv::Mat image, cv::String name);

cv::Mat connectAllImages(std::vector<cv::Mat> images);
cv::Mat connectTwoImages(cv::Mat left, cv::Mat right);
cv::Point findPoint(cv::Mat left, cv::Mat right, int tX, int tY, int tWidht, int tHeight);

cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int diff);
cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int lowerDiff, int upperDiff);
cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int hueTolerance, int saturationTolerance, int valueTolerance);
cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int lowerHueTolerance, int lowerSaturationTolerance, int lowerValueTolerance, int upperHueTolerance, int upperSaturationTolerance, int upperValueTolerance);
cv::Vec3b convertRGBtoHSV(cv::Scalar rgb);
