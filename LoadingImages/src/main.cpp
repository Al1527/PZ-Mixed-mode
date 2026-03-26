
#include <opencv2/opencv.hpp>
#include "config.h"
#include "imagesManager.h"
#include "windowManager.h"
#include "contour.h"

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

  cv::Mat output = windowManager.drawWindow(connectedImages, config);
  putImageToDirectory("output", output, "output"); 

  std::vector<Contour> contours = windowManager.createContourWindow(output, config);

  for (int i = 0; i < contours.size(); i++){
    contours[i].addContourToGeoJson(output, config.freqOfPointsInContour, "output");
  }
  
  return 0; 
}


