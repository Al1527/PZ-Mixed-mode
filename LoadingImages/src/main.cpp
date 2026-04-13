
#include <opencv2/opencv.hpp>
#include "config.h"
#include "imagesManager.h"
#include "windowManager.h"

int main() {
 
  WindowManager windowManager;
  Config config;
  config.clearFolder("output");
  config.load("config.json");
  config.checkConfiguration();

  std::vector<cv::Mat> images;
  loadImages("images", images);
  config.checkFormat(images.size());

  cv::Scalar pickedColor = windowManager.pickColorWindow(images[0]);

  std::vector<cv::Mat> convertedImages = windowManager.removeColorWindow(images, config, pickedColor);

  cv::Mat connectedImages = connectAllImages(convertedImages, {config.imageFormatColumns, config.imageFormatRows});

  cv::Mat buf = windowManager.drawWindow(connectedImages, config);
 
  cv::Mat output = windowManager.fixGapsInContourWindow(buf);
  
  putImageToDirectory("output", output, "output"); 
  
  return 0; 
}


