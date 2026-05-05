#include "imagesManager.h"
#include "opencv2/core.hpp"
#include "opencv2/core/cvstd.hpp"
#include "opencv2/core/hal/interface.h"
#include "opencv2/core/types.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgcodecs.hpp"
#include <opencv2/ximgproc.hpp>
#include <string>
#include <vector>

cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int diff){
  cv::Scalar lowerb(std::max(0.0, rgb[2] - diff), std::max(0.0, rgb[1] - diff), std::max(0.0, rgb[0] - diff));
  cv::Scalar upperb(std::min(255.0, rgb[2] + diff), std::min(255.0, rgb[1] + diff), std::min(255.0, rgb[0] + diff));

  cv::Mat out;
  cv::inRange(img, lowerb, upperb, out);
  return out;
}

cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int lowerDiff, int upperDiff){
  cv::Scalar lowerb(std::max(0.0, rgb[2] - lowerDiff), std::max(0.0, rgb[1] - lowerDiff), std::max(0.0, rgb[0] - lowerDiff));
  cv::Scalar upperb(std::min(255.0, rgb[2] + upperDiff),std::min(255.0, rgb[1] + upperDiff), std::min(255.0, rgb[0] + upperDiff));
  
  cv::Mat out;
  cv::inRange(img, lowerb, upperb, out);
  return out;
}


cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int hueTolerance, int saturationTolerance, int valueTolerance) {
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

cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int lowerHueTolerance, int lowerSaturationTolerance,
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

cv::Vec3b convertRGBtoHSV(cv::Scalar rgb){
  cv::Mat bgrPixel(1, 1, CV_8UC3);
  bgrPixel.at<cv::Vec3b>(0,0) = cv::Vec3b(rgb[2], rgb[1],rgb[0]);
  cv::Mat hsvPixel;
  cv::cvtColor(bgrPixel, hsvPixel, cv::COLOR_BGR2HSV);
  return hsvPixel.at<cv::Vec3b>(0,0);
}

void loadImages(std::filesystem::path directoryPath, std::vector<cv::Mat> &images){
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

void showImage(cv::Mat image, cv::String name){
  cv::imshow(name, image);
  cv::waitKey(0);
  cv::destroyAllWindows();
}
  
void putImagesToDirectory(std::filesystem::path directoryPath, std::vector<cv::Mat> images){
  if (!std::filesystem::exists(directoryPath)){
    std::cout << "Error: Nie znaleziono folderu";
    return;
  }
  
  for (int i = 0; i < images.size(); i++){
    std::filesystem::path filePath = directoryPath / (std::to_string(i) + ".png");
    cv::imwrite(filePath.string(), images[i], {cv::IMWRITE_PNG_COMPRESSION, 0});
  }
}

void putImageToDirectory(std::filesystem::path directoryPath, cv::Mat image, std::string name){
  if (!std::filesystem::exists(directoryPath)){
    std::cout << "Error: Nie znaleziono folderu";
    return;
  }
  std::filesystem::path filePath = directoryPath / (name + ".png");
  cv::imwrite(filePath.string(), image, {cv::IMWRITE_PNG_COMPRESSION, 0});
}

cv::Point findPoint(cv::Mat left, cv::Mat right, int tX, int tY, int tWidht, int tHeight){
  cv::Rect rec(tX, tY, tWidht, tHeight);
  cv::Mat imgTemplate = right(rec).clone();

  cv::Mat result;
  cv::matchTemplate(left, imgTemplate, result, cv::TM_CCOEFF_NORMED);

  double minVal, maxVal;
  cv::Point minLoc, maxLoc;
  cv::minMaxLoc(result, &minVal, &maxVal, &minLoc, &maxLoc);

  return maxLoc;
}

cv::Mat connectTwoImagesHorizontally(cv::Mat left, cv::Mat right){
  cv::Point match = findPoint(left, right, 0, right.rows / 4, 40, right.rows / 2);

  int diffY = match.y - (right.rows / 4);
  int minY = std::max(0, diffY);
  int maxY = std::min(left.rows, diffY + right.rows);

  int outputWidth  = match.x + right.cols;
  int outputHeight = maxY - minY;

  cv::Mat output(outputHeight, outputWidth, left.type());

  left(cv::Rect(0, minY, left.cols, outputHeight))
  .copyTo(output(cv::Rect(0, 0, left.cols, outputHeight)));

  right(cv::Rect(0, minY - diffY, right.cols, outputHeight))
  .copyTo(output(cv::Rect(match.x, 0, right.cols, outputHeight)));

  return output;
}

cv::Mat connectTwoImagesVertically(cv::Mat left, cv::Mat right){
  cv::Point match = findPoint(left, right, right.cols / 4, 0, right.cols / 2, 40);

  int diffX = match.x - (right.cols / 4);
  int minX = std::max(0, diffX);
  int maxX = std::min(left.cols, diffX + right.cols);
  
  int outputWidth = maxX - minX;
  int outputHeight = match.y + right.rows;

  cv::Mat output(outputHeight, outputWidth, left.type());

  left(cv::Rect(minX, 0, outputWidth, match.y))
  .copyTo(output(cv::Rect(0, 0, outputWidth, match.y)));

  right(cv::Rect(minX - diffX, 0, outputWidth, right.rows))
  .copyTo(output(cv::Rect(0, match.y, outputWidth, right.rows)));

  return output;
}
  
cv::Mat connectAllImages(std::vector<cv::Mat> images, std::pair<int, int> option){
  std::vector<cv::Mat> rows;
  
  for (int i = 0; i < images.size(); i += option.second){
    cv::Mat buf = images[i];
    for (int j = i + 1; j < i + option.second; j++){
      buf = connectTwoImagesHorizontally(buf, images[j]);
    }
    rows.push_back(buf);
  }

  cv::Mat output = rows[0];

  for (int i = 1; i <rows.size(); i++){
    output = connectTwoImagesVertically(output, rows[i]);
  }

  return output;
}

cv::Mat morphologyClosing(cv::Mat image, int size, int e){
  cv::Mat output;

  cv::Mat element = cv::getStructuringElement(e, cv::Size((2 * size) + 1, (2 * size) + 1));

  cv::morphologyEx(image, output, cv::MORPH_CLOSE, element);

  return output;
}

cv::Mat skeletonization(cv::Mat image, int size, int e){
  if (size == 0){
    return image;
  }
  cv::Mat element = cv::getStructuringElement(e, cv::Size((2 * size) + 1, (2 * size) + 1));
  cv::Mat buf;

  cv::dilate(image, buf, element, cv::Point(-1,-1), 1);
  cv::Mat output;

  cv::ximgproc::thinning(buf, output, cv::ximgproc::THINNING_ZHANGSUEN);

  return output;
}

cv::Mat morphologyOpening(cv::Mat image, int size){
  cv::Mat output;

  cv::Mat element = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(size, size));

  cv::morphologyEx(image, output, cv::MORPH_OPEN, element);
  
  return output;
}
