
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

  cv::Mat connectedImages = connectAllImages(images, {config.imageFormatColumns, config.imageFormatRows});

  cv::Scalar pickedColor = windowManager.pickColorWindow(connectedImages);

  cv::Mat convertedImage = windowManager.removeColorWindow(connectedImages, config, pickedColor);

  cv::Mat output = windowManager.fixGapsInContourWindow2(convertedImage, config);
  
  putImageToDirectory("output", output, "output"); 
  
  return 0; 
}


