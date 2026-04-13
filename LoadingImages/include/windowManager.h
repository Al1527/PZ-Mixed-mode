
#pragma once

#include "contour.h"
#include "opencv2/core/mat.hpp"
#include "config.h"
#include "opencv2/core/types.hpp"
#include <vector>

struct HueParameters{
  int lowHue = 0, lowSaturation = 0, lowValue = 0;
  int highHue = 0, highSaturation = 0, highValue = 0;
};

class WindowManager{
  public:
    cv::Mat img;
    cv::Scalar pickedColor;
    std::vector<Contour> contours;
    std::vector<cv::Mat> images;
    HueParameters hueParameters;
    cv::Scalar rgb;
    int height = 0;
    int basedHeight = 0;
    int scaleHeight = 1;
    int size = 1;
    int colorChosed = 1;
    int morph_elem = 0;
    int morph_size = 0;

    cv::Scalar pickColorWindow(cv::Mat &img);
    std::vector<cv::Mat> removeColorWindow(std::vector<cv::Mat>& images, Config &config, cv::Scalar rgb);
    cv::Mat drawWindow(cv::Mat &img, Config &config);
    std::vector<Contour> createContourWindow(cv::Mat &img, Config& config); 
    cv::Mat fixGapsInContourWindow(cv::Mat img); 

  private:

    static void createContour(int event, int x, int y, int, void *userdata);
    static void getColor(int event, int x, int y, int, void* userdata);
    static void drawPixelWhite(int event, int x, int y, int, void* userdata);
    static void drawRectengle(cv::Mat& img, int x, int y, int size, int color);
};
