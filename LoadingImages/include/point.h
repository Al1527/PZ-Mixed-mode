
#pragma once
#include <filesystem>
#include <vector>

class Point{
  public:
    int x;
    int y;
    double height;

    Point(int x, int y, double h);
};

void createGeoJson(std::vector<Point> &points, std::filesystem::path directoryPath);
