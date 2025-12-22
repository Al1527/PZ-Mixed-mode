#include "imagesManager.h"
#include "opencv2/core.hpp"
#include "opencv2/core/hal/interface.h"
#include "opencv2/core/types.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgcodecs.hpp"
#include <string>

cv::Mat ImagesManager::removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int diff){
  cv::Scalar lowerb(std::max(0.0, rgb[2] - diff), std::max(0.0, rgb[1] - diff), std::max(0.0, rgb[0] - diff));
  cv::Scalar upperb(std::min(255.0, rgb[2] + diff), std::min(255.0, rgb[1] + diff), std::min(255.0, rgb[0] + diff));

  cv::Mat out;
  cv::inRange(img, lowerb, upperb, out);
  return out;
}

cv::Mat ImagesManager::removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int lowerDiff, int upperDiff){
  cv::Scalar lowerb(std::max(0.0, rgb[2] - lowerDiff), std::max(0.0, rgb[1] - lowerDiff), std::max(0.0, rgb[0] - lowerDiff));
  cv::Scalar upperb(std::min(255.0, rgb[2] + upperDiff),std::min(255.0, rgb[1] + upperDiff), std::min(255.0, rgb[0] + upperDiff));
  
  cv::Mat out;
  cv::inRange(img, lowerb, upperb, out);
  return out;
}


cv::Mat ImagesManager::removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int hueTolerance, int saturationTolerance, int valueTolerance) {
  cv::Mat imageHSV;
  cv::cvtColor(img, imageHSV, cv::COLOR_BGR2HSV);

  cv::Vec3b hsv = convertRGBtoHSV(rgb);

  int h = hsv[0]; int s = hsv[1]; int v = hsv[2];

  cv::Scalar lowerb(std::max(0, h - hueTolerance), std::max(0, s - saturationTolerance), std::max(0, v - valueTolerance));
  cv::Scalar upperb(std::min(179, h + hueTolerance), std::min(255, s + saturationTolerance), std::min(255, v + valueTolerance));
  cv::Mat out;
  cv::inRange(imageHSV, lowerb, upperb, out);
  
  return out;
}

cv::Mat ImagesManager::removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int lowerHueTolerance, int lowerSaturationTolerance,
                    int lowerValueTolerance, int upperHueTolerance, int upperSaturationTolerance, int upperValueTolerance){

  cv::Mat imageHSV;
  cv::cvtColor(img, imageHSV, cv::COLOR_BGR2HSV);

  cv::Vec3b hsv = convertRGBtoHSV(rgb);

  int h = hsv[0]; int s = hsv[1]; int v = hsv[2];

  cv::Scalar lowerb(std::max(0, h - lowerHueTolerance), std::max(0, s - lowerSaturationTolerance),std::max(0, v - lowerValueTolerance));
  cv::Scalar upperb(std::min(179, h + upperHueTolerance), std::min(255, s + upperSaturationTolerance), std::min(255, v + upperValueTolerance));

  cv::Mat out;
  cv::inRange(imageHSV, lowerb, upperb, out);
  return out;
}

cv::Vec3b ImagesManager::convertRGBtoHSV(cv::Scalar rgb){
  cv::Mat bgrPixel(1, 1, CV_8UC3);
  bgrPixel.at<cv::Vec3b>(0,0) = cv::Vec3b(rgb[2], rgb[1],rgb[0]);
  cv::Mat hsvPixel;
  cv::cvtColor(bgrPixel, hsvPixel, cv::COLOR_BGR2HSV);
  return hsvPixel.at<cv::Vec3b>(0,0);
}

cv::Mat ImagesManager::getImagesByIndex(int index){
  if (index < 0 || index >= images.size()){
    std::cout << "Error: podano zly indeks";
    return cv::Mat();
  }
  return images[index];
}

void ImagesManager::loadImages(std::filesystem::path directoryPath){
  if (!std::filesystem::exists(directoryPath)){
    std::cout << "Error: Nie znaleziono folderu";
    return;
  } 
  std::vector<std::filesystem::path> filePaths;
  
  for (const auto& entry : std::filesystem::directory_iterator(directoryPath)){
    filePaths.push_back(entry.path());
  }
  std::sort(filePaths.begin(), filePaths.end()); // sortujemy by kolejnosc byla taka sama jak w folderze

  for (const auto& path : filePaths) {
    cv::Mat image = cv::imread(path.string(), cv::IMREAD_UNCHANGED);
    images.push_back(image);
  }
}

void ImagesManager::showImage(cv::Mat image){
  cv::imshow("Image: ", image);
  cv::waitKey(0);
  cv::destroyAllWindows();
}
  
void ImagesManager::putImagesToDirectory(std::filesystem::path directoryPath, std::vector<cv::Mat> images){
  if (!std::filesystem::exists(directoryPath)){
    std::cout << "Error: Nie znaleziono folderu";
    return;
  }
  
  for (int i = 0; i < images.size(); i++){
    std::filesystem::path filePath = directoryPath / (std::to_string(i) + ".png");
    cv::imwrite(filePath.string(), images[i], {cv::IMWRITE_PNG_COMPRESSION, 0});
  }
}

void ImagesManager::putImageToDirectory(std::filesystem::path directoryPath, cv::Mat image, std::string name){
  if (!std::filesystem::exists(directoryPath)){
    std::cout << "Error: Nie znaleziono folderu";
    return;
  }
  std::filesystem::path filePath = directoryPath / (name + ".png");
  cv::imwrite(filePath.string(), image, {cv::IMWRITE_PNG_COMPRESSION, 0});
}

cv::Point ImagesManager::findPoint(cv::Mat left, cv::Mat right, int tX, int tY, int tWidht, int tHeight){
  cv::Rect rec(tX, tY, tWidht, tHeight);
  cv::Mat imgTemplate = right(rec).clone();

  cv::Mat result;
  cv::matchTemplate(left, imgTemplate, result, cv::TM_CCOEFF_NORMED);

  double minVal, maxVal;
  cv::Point minLoc, maxLoc;
  cv::minMaxLoc(result, &minVal, &maxVal, &minLoc, &maxLoc);

  return maxLoc;
}

cv::Mat ImagesManager::connectTwoImages(cv::Mat left, cv::Mat right){
  cv::Point match = findPoint(left, right, 0, right.rows / 4, 40, right.rows / 2); 

  int diffY = match.y - (right.rows / 4);

  int minY = std::min(0, diffY);
  int maxY = std::max(left.rows, diffY + right.rows);

  int outputWidth  = match.x + right.cols;
  int outputHeight = maxY - minY;

  cv::Mat output(outputHeight, outputWidth, left.type(), cv::Scalar(0, 0, 0));

  left.copyTo(output(cv::Rect(0, -minY, left.cols, left.rows)));
  right.copyTo(output(cv::Rect(match.x, diffY - minY, right.cols, right.rows)));

  return output;
}
  
cv::Mat ImagesManager::connectAllImages(std::vector<cv::Mat> images){
  cv::Mat output = images[0];

  for (int i = 1; i < images.size(); i++){
    output = connectTwoImages(output, images[i]); 
  }
  return output;
}

