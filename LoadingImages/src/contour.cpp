#include "contour.h"
#include "json.hpp"
#include "iostream"
#include <stack>
#include <vector>
#include "fstream"


Contour::Contour(cv::Mat &img, int x, int y, double h){
  height = h; 

  int tabx[8] = {1, -1, 0, 0,  1, 1, -1, -1};
  int taby[8] = {0, 0, 1, -1,  1, -1, 1, -1};
  std::stack<std::pair<int, int>> s;
  s.push({x, y});

  while (!s.empty()){
    std::pair<int, int> buf = s.top();
    s.pop();

    if ((buf.first >= 0) && (buf.second >= 0) && (buf.second < img.rows) && (buf.first < img.cols)){
      uchar &pix = img.at<uchar>(buf.second, buf.first);
      if (pix == 255){
        pix = 100;
        pixelsInCountour.insert(buf);

        for (int i = 0; i < 8; i++){
          s.push({buf.first + tabx[i], buf.second + taby[i]});
        }
      } 
    }
  }
}

void Contour::addContourToGeoJson(cv::Mat& img, int freq, std::filesystem::path directoryPath){
  std::vector<std::pair<int, int>> vec;

  int xFreq = img.cols / freq;
  int yFreq = img.rows / freq;

  for (int i = 0; i < img.cols; i += xFreq){
    for (int j = 0; j < img.rows; j += yFreq){
      if (pixelsInCountour.find({i, j}) != pixelsInCountour.end()){
        vec.push_back({i, j});
      }
    }
  }

  if (vec.size() < 2) {
    std::cout << "Error: Znaleziono za malo punktow, nie mozna stworzyc poziomicy";
    return;
  }

  std::filesystem::path filePath = directoryPath / "contours.geojson";
  nlohmann::json geojson;

  if (std::filesystem::exists(filePath)) {
      std::ifstream inFile(filePath);
      inFile >> geojson;
      inFile.close();
  } else {
      geojson["type"] = "FeatureCollection";
      geojson["features"] = nlohmann::json::array();
  }

  nlohmann::json coordinates = nlohmann::json::array();
  for (const auto& p : vec) {
      coordinates.push_back({p.first, p.second});
  }

  nlohmann::json feature;
  feature["type"] = "Feature";
  feature["properties"] = {
      {"elevation", height}
  };
  feature["geometry"] = {
      {"type", "LineString"},
      {"coordinates", coordinates}
  };
  geojson["features"].push_back(feature);

  std::ofstream outFile(filePath);
  outFile << geojson.dump(4);
}
