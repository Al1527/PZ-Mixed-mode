
#include "windowManager.h"
#include "opencv2/highgui.hpp"
#include <iostream>
#include <vector>
#include "imagesManager.h"

cv::Scalar WindowManager::pickColorWindow(cv::Mat &img){
  if (img.channels() == 1) {
      cv::cvtColor(img, img, cv::COLOR_GRAY2BGR);
  } else if (img.channels() == 4) {
      cv::cvtColor(img, img, cv::COLOR_BGRA2BGR);
  }
  this->img = img;
  cv::namedWindow("pickColorWindow");
  cv::setMouseCallback("pickColorWindow", getColor, this);
  while (true){
    cv::imshow("pickColorWindow", img);

    int key = cv::waitKey(10);
    if (key == 27)
        break;
  }
  cv::destroyAllWindows();
  return this->pickedColor;
}

void WindowManager::getColor(int event, int x, int y, int, void* userdata){
  auto* self = reinterpret_cast<WindowManager*>(userdata);
  if (event == cv::EVENT_LBUTTONDOWN){
    if (x >= 0 && x < self->img.cols && y >= 0 && y < self->img.rows){
      cv::Vec3b color = self->img.at<cv::Vec3b>(y, x); 
      self->pickedColor = cv::Scalar(color[2], color[1], color[0]);
      std::cout << "RGB: " << (int)color[2] << " " << (int)color[1] << " " << (int)color[0] << std::endl;
    } 
  }
}


std::vector<cv::Mat> WindowManager::removeColorWindow(std::vector<cv::Mat>& images, cv::Scalar rgb){
  std::vector<cv::Mat> convertedImages;
  cv::namedWindow("removeWindow");
  cv::createTrackbar("Low H",  "removeWindow", &hueParameters.lowHue, 179);
  cv::createTrackbar("High H", "removeWindow", &hueParameters.highHue, 179);
  cv::createTrackbar("Low S",  "removeWindow", &hueParameters.lowSaturation, 255);
  cv::createTrackbar("High S", "removeWindow", &hueParameters.highSaturation, 255);
  cv::createTrackbar("Low V",  "removeWindow", &hueParameters.lowValue, 255);
  cv::createTrackbar("High V", "removeWindow", &hueParameters.highValue, 255);

  cv::Mat img = images[0]; 
  cv::Mat img_HSV, img_threshold;

  cv::Vec3b hsv = convertRGBtoHSV(rgb);
  int h = hsv[0]; int s = hsv[1]; int v = hsv[2];

  while (true) {
    cv::cvtColor(img, img_HSV, cv::COLOR_BGR2HSV);
    cv::Scalar lower(std::max(h - hueParameters.lowHue, 0), std::max(s - hueParameters.lowSaturation, 0),
        std::max(v - hueParameters.lowValue, 0));
    cv::Scalar upper(std::min(h + hueParameters.highHue, 179), std::min(s + hueParameters.highSaturation, 255),
        std::min(v + hueParameters.highValue, 255));

    cv::inRange(img_HSV, lower, upper, img_threshold);
    cv::imshow("removeWindow", img_threshold);

    char key = (char) cv::waitKey(30);
    if (key == 'q' || key == 27){
      cv::destroyAllWindows();
      break;
    }
  }

  for (int i = 0; i < images.size(); i++){
    convertedImages.push_back(removeAllOtherColors(images[i], rgb, hueParameters.lowHue, hueParameters.lowSaturation,
          hueParameters.lowValue, hueParameters.highHue, hueParameters.highSaturation, hueParameters.highValue));
  }

  return convertedImages;
}

cv::Mat WindowManager::removeColorWindow(cv::Mat image, cv::Scalar rgb){
  cv::namedWindow("removeWindow");
  cv::createTrackbar("Low H",  "removeWindow", &hueParameters.lowHue, 179);
  cv::createTrackbar("High H", "removeWindow", &hueParameters.highHue, 179);
  cv::createTrackbar("Low S",  "removeWindow", &hueParameters.lowSaturation, 255);
  cv::createTrackbar("High S", "removeWindow", &hueParameters.highSaturation, 255);
  cv::createTrackbar("Low V",  "removeWindow", &hueParameters.lowValue, 255);
  cv::createTrackbar("High V", "removeWindow", &hueParameters.highValue, 255);

  cv::Mat img = image.clone(); 
  cv::Mat img_HSV, img_threshold;

  cv::Vec3b hsv = convertRGBtoHSV(rgb);
  int h = hsv[0]; int s = hsv[1]; int v = hsv[2];

  while (true) {
    cv::cvtColor(img, img_HSV, cv::COLOR_BGR2HSV);
    cv::Scalar lower(std::max(h - hueParameters.lowHue, 0), std::max(s - hueParameters.lowSaturation, 0),
        std::max(v - hueParameters.lowValue, 0));
    cv::Scalar upper(std::min(h + hueParameters.highHue, 179), std::min(s + hueParameters.highSaturation, 255),
        std::min(v + hueParameters.highValue, 255));

    cv::inRange(img_HSV, lower, upper, img_threshold);
    cv::imshow("removeWindow", img_threshold);

    char key = (char) cv::waitKey(30);
    if (key == 'q' || key == 27){
      cv::destroyAllWindows();
      break;
    }
  }

  return removeAllOtherColors(img, rgb, hueParameters.lowHue, hueParameters.lowSaturation,
        hueParameters.lowValue, hueParameters.highHue, hueParameters.highSaturation, hueParameters.highValue);
}


cv::Mat WindowManager::drawWindow(cv::Mat &img){
  this->img = img;
  cv::namedWindow("drawWindow");
  int trackbarSize = 5;
  cv::createTrackbar("Size ", "drawWindow", &trackbarSize, 20);
  cv::setMouseCallback("drawWindow", drawPixelWhite, this);
  while (true) {
    size = trackbarSize;
    cv::imshow("drawWindow", img);
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

  return img;
}

void WindowManager::drawPixelWhite(int event, int x, int y, int flags, void* userdata){
  auto* self = reinterpret_cast<WindowManager*>(userdata);

  if (flags & cv::EVENT_FLAG_LBUTTON){
    if (x >= 0 && x < self->img.cols && y >= 0 && y < self->img.rows && self->drawMode){
      int color = (self->colorChosed == 1) ? 255 : 0;

      drawCircle(self->img, x, y, self->size, color);
    }
  }
}

void WindowManager::drawRectengle(cv::Mat& img, int x, int y, int size, int color){
  for (int i = y-size; i < y+size; i++){
    for (int j = x-size; j < x+size; j++){
      if (j >=0 && j < img.cols && i >=0 && i < img.rows){
          img.at<uchar>(i,j) = color;
      }
    }
  }
}

void WindowManager::drawCircle(cv::Mat& img, int x, int y, int size, int color){
  for (int i = y-size; i < y+size; i++){
    for (int j = x-size; j < x+size; j++){
      if (j >= 0 && j < img.cols && i >= 0 && i < img.rows){
        if ((j-x)*(j-x) + (i -y)*(i-y) <= size*size){
          img.at<uchar>(i, j) = color;
        }
      }
    }
  }
}


cv::Mat WindowManager::fixGapsInContourWindow(cv::Mat img){
  cv::Mat output;
  cv::namedWindow("fixGapsInContour");

  cv::createTrackbar("0-Rect 1-Cross 2-Ellipse 3-Diamond", "fixGapsInContour", &morph_elem, 3);
 
  cv::createTrackbar("size- ", "fixGapsInContour",&morph_size, 21);

  while (true) {
    output = skeletonization(img,  morph_size + 1, morph_elem);
    cv::imshow("fixGapsInContour", output);

    char key = (char) cv::waitKey(30);
    if (key == 'q' || key == 27){
      cv::destroyAllWindows();
      break;
    }
  }
    
  return output;
}


cv::Mat WindowManager::fixGapsInContourWindow2(cv::Mat img){
  std::vector<cv::Mat> stages;
  this->img = img.clone();
  stages.push_back(this->img.clone());
  cv::Mat buf;

  cv::namedWindow("drawWindow");
  int trackbarSize = 5;
  cv::createTrackbar("SIZE OF BRUSH: ", "drawWindow", &trackbarSize, 20);
  cv::setMouseCallback("drawWindow", drawPixelWhite, this);
  cv::createTrackbar("SKELETONIZATION SIZE: ", "drawWindow", &morph_size, 21);

  while (true) {
    size = trackbarSize;
    int key = cv::waitKey(10);
    if (drawMode){
      cv::displayStatusBar("drawWindow", "DRAW MODE - d   CHANGE BRUSH - c   SKELETONIZATION MODE - s   ADD CHANGES - a   UNDO - b   EXIT - esc   CURRENT MODE - DRAW MODE", 0);
      cv::imshow("drawWindow", this->img);
      if (key == 'c'){
        if (colorChosed == 1){
          colorChosed = 0;
        } else {
          colorChosed = 1;
        }
      }
    } else {
      buf = skeletonization(this->img,  morph_size, 2);
      cv::displayStatusBar("drawWindow", "DRAW MODE - d   CHANGE BRUSH - c   SKELETONIZATION MODE - s   ADD CHANGES - a   UNDO - b   EXIT - esc   CURRENT MODE - SKELETONIZATION MODE", 0);
      cv::imshow("drawWindow", buf);
    }
    
    if (key == 'b' && !stages.empty()){
      this->img = stages.back();
      stages.pop_back();
    }

    if (key == 'd'){
      drawMode = true;
      if (stages.size() <= 30){
        stages.push_back(this->img.clone());
      }
    }

    if (key == 's'){
      drawMode = false;
      if (stages.size() <= 30){
        stages.push_back(this->img.clone());
      }
    }

    if (key == 'a' && !buf.empty()){
      if (stages.size() <= 30){
        stages.push_back(this->img.clone());
      }
      morph_size = 0;
      cv::setTrackbarPos("SKELETONIZATION SIZE: ", "drawWindow", 0);
      this->img = buf.clone();
    }

    if (key == 27){
      break;
    }
  }
  cv::destroyAllWindows();

  return this->img;
}
