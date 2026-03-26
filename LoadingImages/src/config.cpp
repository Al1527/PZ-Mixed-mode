#include "config.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include "json.hpp"


Config::Config(){
  imageFormatColumns = 1;
  imageFormatRows = 1;
  scaleOfHeight = 0;
  minContourHeight = 0;
  maxContourHeight = 1000;
  maxToleranceOfColor = 100;
  freqOfPointsInContour = 100;
}

void Config::load(std::string filename){
  std::ifstream file(filename);
  if (!file.is_open()){
    std::cout << "Error: blad podczas otwierania pliku";
    return;
  }

  nlohmann::json data = nlohmann::json::parse(file);

  imageFormatColumns = data["imageFormat"].value("columns", 1);
  imageFormatRows = data["imageFormat"].value("rows", 1);
  scaleOfHeight = data["contour"].value("scaleOfHeight", 1);
  minContourHeight = data["contour"].value("minHeight", 0); 
  maxContourHeight = data["contour"].value("maxHeight", 100); 
  maxToleranceOfColor = data["contour"].value("maxToleranceOfColor", 100); 
  freqOfPointsInContour = data["contour"].value("freqOfPoints", 100); 
}

void Config::clearFolder(std::filesystem::path folderPath){

  if (!std::filesystem::exists(folderPath)) {
    std::cout << "Error: blad czyszczenia folderu" << std::endl;
    return;
  }

  for (const auto& entry : std::filesystem::directory_iterator(folderPath)){
    std::filesystem::remove(entry.path());
  }
}

bool Config::checkConfiguration(){

  if (minContourHeight >= maxContourHeight){
    std::cout << "Error Config: podano zle wartosci dla wysokosci poziomicy";
    return false;
  }

  if (freqOfPointsInContour <= 0){
    std::cout << "Error Config: podano zla czestotliowsc znajdowania punktow w poziomicy";
    return false;
  }

  if (maxToleranceOfColor <= 0){
    std::cout << "Error Config: za mala tolerancja koloru";
    return false;
  }
  
  return true;
}

bool Config::checkFormat(int numberOfImages){
 
  if (imageFormatColumns * imageFormatRows != numberOfImages){
    std::cout << "Error Config: zly format zdjec";
    return false;
  }

  return true;
}
