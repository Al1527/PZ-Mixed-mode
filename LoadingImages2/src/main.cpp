
#include <opencv2/opencv.hpp>
#include "imagesManager.h"
#include "windowManager.h"

int main() {
 
  WindowManager windowManager;
  int imageFormatRows = 1;
  int imageFormatColumns = 1;

  clearFolder("output");

  std::vector<cv::Mat> images;
  loadImages("images", images);

  if (imageFormatRows * imageFormatColumns != images.size()){
    std::cout << "Error: Podano zły format" << std::endl;
  }

  cv::Mat connectedImages = connectAllImages(images, {imageFormatColumns, imageFormatRows});

  cv::Scalar pickedColor = windowManager.pickColorWindow(connectedImages);

  cv::Mat convertedImage = windowManager.removeColorWindow(connectedImages, pickedColor);

  cv::Mat output = windowManager.fixGapsInContourWindow2(convertedImage);
  
  putImageToDirectory("output", output, "output"); 
  
  return 0; 
}


