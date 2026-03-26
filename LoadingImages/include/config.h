#pragma once

#include <filesystem>
#include<string>

class Config{
  public:
    int imageFormatColumns;
    int imageFormatRows;
    int scaleOfHeight;
    int minContourHeight;
    int maxContourHeight;
    int maxToleranceOfColor;
    int freqOfPointsInContour;

    Config();

    void load(std::string filename);
    void clearFolder(std::filesystem::path folderPath);
    bool checkConfiguration();
    bool checkFormat(int numberOfImages);
};
