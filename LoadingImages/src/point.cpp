
#include "point.h"
#include "json.hpp"
#include <iostream>
#include "fstream"

Point::Point(int x, int y, double h){
  this->x = x;
  this->y = y;
  this->height = h;
}


void createGeoJson(std::vector<Point> &points, std::filesystem::path directoryPath){
  nlohmann::json j;
  j["type"] = "FeatureCollection";
  j["features"] = nlohmann::json::array();
  std::filesystem::path filePath = directoryPath / "points.geojson";
  std::ofstream file(filePath, std::ios::out);

  if (!file.is_open()){
    std::cout << "Error: Nie mozna otworzyc pliku";
    return;
  }

  for (Point &p : points) {
    nlohmann::json feature;
    feature["type"] = "Feature";
    feature["geometry"] = {
        {"type", "Point"},
        {"coordinates", {p.x, p.y, p.height}}
    };
    feature["properties"] = nlohmann::json::object(); 
    j["features"].push_back(feature);
  }
  file << j.dump(4);
  file.close();
}


