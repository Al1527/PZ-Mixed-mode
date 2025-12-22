#include <opencv2/opencv.hpp>
#include <filesystem>
#include "imagesManager.h"

int main() {
  
  ImagesManager im;
  im.loadImages("images");
  
  std::vector<cv::Mat> convertedImages;

  cv::Scalar rgb(175, 172, 141);

  for (int i = 0; i < im.images.size(); i++){
    convertedImages.push_back(im.removeAllOtherColors(im.images[i], rgb, 15));
  }

  cv::Mat out = im.connectAllImages(convertedImages);
  im.putImageToDirectory("output", out, "output"); 

  return 0;
}

