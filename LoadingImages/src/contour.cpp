#include "contour.h"
#include <stack>
#include <vector>

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
        pixelsInCountour.push_back(buf);

        for (int i = 0; i < 8; i++){
          s.push({buf.first + tabx[i], buf.second + taby[i]});
        }
      } 
    }
  }
}

void Contour::createPoints(cv::Mat &img, std::vector<Point> &points, int freq){
  int xFreq = img.cols / freq;
  int yFreq = img.rows / freq;
  
  for (int i = 0; i < img.cols; i += xFreq){
    for (int j = 0; j < img.rows; j += yFreq){
      if (std::find(pixelsInCountour.begin(), pixelsInCountour.end(), std::make_pair(i,j)) != pixelsInCountour.end()){
        points.push_back(Point(i, j, height));
      }
    }
  }
}
