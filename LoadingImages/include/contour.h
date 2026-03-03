#pragma once

#include "opencv2/core/mat.hpp"
#include <set>
#include <filesystem>

class Contour{
  public:
    std::set<std::pair<int,int>> pixelsInCountour;
    double height;

    Contour(cv::Mat &img, int x, int y, double height);

    void addContourToGeoJson(cv::Mat& img, int freq, std::filesystem::path directoryPath);
};
