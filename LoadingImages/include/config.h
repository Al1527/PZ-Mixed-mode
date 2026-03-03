#pragma once

#include<string>

class Config{
  public:
    int imageFormatColumns;
    int imageFormatRows;
    int minContourHeight;
    int maxContourHeight;
    int maxToleranceOfColor;
    int freqOfPointsInContour;

    Config();

    void load(std::string filename);
    bool checkConfiguration();
    bool checkFormat(int numberOfImages);
};
