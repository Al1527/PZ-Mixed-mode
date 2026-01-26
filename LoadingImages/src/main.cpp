#include <opencv2/opencv.hpp>
#include <filesystem>
#include <vector>
#include "imagesManager.h"
#include "opencv2/core.hpp"
#include "opencv2/highgui.hpp"


std::vector<cv::Mat> images;

const int maxToleranceHue = 100;
const int maxTolerance = 100;

int colorChosed = 1;

int lowHue = 0, lowSaturation = 0, lowValue = 0;
int highHue = 0, highSaturation = 0, highValue = 0;
int size = 1;
cv::Scalar rgb;

static void getColor(int event, int x, int y, int, void* userdata);
static void drawPixelWhite(int event, int x, int y, int, void* userdata);
void drawRectengle(int x, int y, void* userdata, int a, int color);

int main() {
  loadImages("images", images);
  
  std::vector<cv::Mat> convertedImages;

  cv::Mat first = images[0];
  cv::namedWindow("pickColorWindow");
  cv::setMouseCallback("pickColorWindow", getColor, &first);
  showImage(first, "pickColorWindow");

  cv::namedWindow("removeWindow");
  cv::createTrackbar("Low H",  "removeWindow", &lowHue, maxToleranceHue);
  cv::createTrackbar("High H", "removeWindow", &highHue, maxToleranceHue);
  cv::createTrackbar("Low S",  "removeWindow", &lowSaturation, maxTolerance);
  cv::createTrackbar("High S", "removeWindow", &highSaturation, maxTolerance);
  cv::createTrackbar("Low V",  "removeWindow", &lowValue, maxTolerance);
  cv::createTrackbar("High V", "removeWindow", &highValue, maxTolerance);

  cv::Mat img = images[0]; 
  cv::Mat img_HSV, img_threshold;
  
  cv::Vec3b hsv = convertRGBtoHSV(rgb);
  int h = hsv[0]; int s = hsv[1]; int v = hsv[2];

  while (true) {
    cv::cvtColor(img, img_HSV, cv::COLOR_BGR2HSV);
    cv::Scalar lower(std::max(h - lowHue, 0), std::max(s - lowSaturation, 0), std::max(v - lowValue, 0));
    cv::Scalar upper(std::min(h + highHue, 179), std::min(s + highSaturation, 255), std::min(v + highValue, 255));

    cv::inRange(img_HSV, lower, upper, img_threshold);
    cv::imshow("removeWindow", img_threshold);

    char key = (char) cv::waitKey(30);
    if (key == 'q' || key == 27){
      cv::destroyAllWindows();
      break;
    }
  }

  for (int i = 0; i < images.size(); i++){
    convertedImages.push_back(removeAllOtherColors(images[i], rgb, lowHue, lowSaturation, lowValue,
                                                         highHue, highSaturation, highValue));
  }

  cv::namedWindow("drawWindow");
  cv::createTrackbar("Size ", "drawWindow", nullptr, 20);
  cv::Mat out = connectAllImages(convertedImages);
  cv::setMouseCallback("drawWindow", drawPixelWhite, &out);
  while (true) {
    size = cv::getTrackbarPos("Size ", "drawWindow");
    cv::imshow("drawWindow", out);
    int key = cv::waitKey(10);
    if (key == 'c'){
      if (colorChosed == 1){
        colorChosed = 0;
      } else {
        colorChosed = 1;
      }
    }
    if (key == 27)
        break;
  }
  cv::destroyAllWindows();

  putImageToDirectory("output", out, "output");

  return 0; 
}

static void getColor(int event, int x, int y, int, void* userdata){
  if (event == cv::EVENT_LBUTTONDOWN){
    cv::Mat* img = reinterpret_cast<cv::Mat*>(userdata); 

    if (x >= 0 && x < img->cols && y >= 0 && y < img->rows){
      cv::Vec3b color = img->at<cv::Vec3b>(y, x); 
      rgb = cv::Scalar(color[2], color[1], color[0]);
      std::cout << "RGB: " << (int)color[2] << " " << (int)color[1] << " " << (int)color[0] << std::endl;
    } 
  }
}

void drawRectengle(int x, int y, void* userdata, int a, int color){
  cv::Mat* img = reinterpret_cast<cv::Mat*>(userdata);
  for (int i = y-a; i < y+a; i++){
    for (int j = x-a; j < x+a; j++){
      if (j >=0 && j < img->cols && i >=0 && i < img->rows){
        img->at<uchar>(i,j) = color;
      }
    }
  }
}

static void drawPixelWhite(int event, int x, int y, int flags, void* userdata){
  cv::Mat* img = reinterpret_cast<cv::Mat*>(userdata);
  if (flags & cv::EVENT_FLAG_LBUTTON){
    if (x >= 0 && x < img->cols && y >= 0 && y < img->rows){
      if (colorChosed == 1){
        drawRectengle(x, y, userdata, size, 255);
      } else {
        drawRectengle(x, y, userdata, size, 0);
      }
    }
  }
}

