#include "opencv2/core/hal/interface.h"
#include <algorithm>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <filesystem>
#include <vector>

int main() {

  std::vector<cv::Mat> images;
  std::vector<std::pair<int, int>> rowsAndColumns;
  std::filesystem::path directoryPath = "Images";
  std::vector<std::filesystem::path> filePaths;
  cv::Mat connectedImage;
  int numberOfImages = 0;
  int option = 0;
  int imageHeight = 0;
  int imageWidth = 0;
  int connectedImageHeight = 0;
  int connectedImageWidth = 0;


  if (!std::filesystem::exists(directoryPath)){
    std::cout << "Error: Nie znaleziono folderu";
    return 0;
  } 

  for (const auto& entry : std::filesystem::directory_iterator(directoryPath)){
    filePaths.push_back(entry.path());
  }
  std::sort(filePaths.begin(), filePaths.end()); // sortujemy by kolejnosc byla taka sama jak w folderze

  for (const auto& path : filePaths) {
    numberOfImages++;
    cv::Mat image = cv::imread(path.string(), cv::IMREAD_UNCHANGED);
    images.push_back(image);
  }

  imageHeight = images[0].rows;
  imageWidth = images[0].cols;

  for (int i = 1; i <= numberOfImages; i++){
    if (numberOfImages % i == 0){
      rowsAndColumns.push_back({numberOfImages / i,  i});
    }
  }
  
  std::cout << "Wybierz opcje w jaki sposob chcesz zlaczyc zdjecia" << std::endl;
  for (int i = 0; i < rowsAndColumns.size(); i++){
    std::cout << "Opcja " << i << " :" << " " << rowsAndColumns[i].first << " " << rowsAndColumns[i].second << std::endl;
  }
  std::cin >> option;
  
  connectedImageHeight = imageHeight * rowsAndColumns[option].first;
  connectedImageWidth = imageWidth * rowsAndColumns[option].second; 
  connectedImage.create(connectedImageHeight, connectedImageWidth, CV_8UC3);
  
  int imageIterator = 0;
  for (int row = 0; row < rowsAndColumns[option].first; row++){
    for (int col = 0; col < rowsAndColumns[option].second; col++){
      int curr_row = row * imageHeight;
      int curr_col = col * imageWidth;

      images[imageIterator].copyTo(connectedImage(cv::Rect(curr_col, curr_row, imageWidth, imageHeight)));

      imageIterator++;
    }
  }


  cv::imshow("ConnectedImage", connectedImage);
  cv::waitKey(0);
  cv::destroyAllWindows();

  return 0;
}

