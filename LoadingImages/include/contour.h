#pragma once

#include "opencv2/core/mat.hpp"
#include <vector>
#include "point.h"

class Contour{
  public:
    std::vector<std::pair<int,int>> pixelsInCountour;
    double height;

    Contour(cv::Mat &img, int x, int y, double height);

    void createPoints(cv::Mat &img, std::vector<Point>& points, int freq);
};
