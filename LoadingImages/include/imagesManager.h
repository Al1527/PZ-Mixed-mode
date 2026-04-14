#pragma once

#include "opencv2/core/cvstd.hpp"
#include "opencv2/core/types.hpp"
#include <opencv2/opencv.hpp>
#include <vector>
#include <filesystem>

void putImagesToDirectory(std::filesystem::path directoryPath, std::vector<cv::Mat> images);
void putImageToDirectory(std::filesystem::path directoryPath, cv::Mat image, std::string name);
void loadImages(std::filesystem::path directoryPath, std::vector<cv::Mat> &images);
void showImage(cv::Mat image, cv::String name);

cv::Mat connectAllImages(std::vector<cv::Mat> images, std::pair<int, int> option);
cv::Mat connectTwoImagesHorizontally(cv::Mat left, cv::Mat right);
cv::Mat connectTwoImagesVertically(cv::Mat left, cv::Mat right);
cv::Point findPoint(cv::Mat left, cv::Mat right, int tX, int tY, int tWidht, int tHeight);

cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int diff);
cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int lowerDiff, int upperDiff);
cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int hueTolerance, int saturationTolerance, int valueTolerance);

/**
 * @brief Usuwa wszystkie inne kolory ze zdjęcia nie pasujące do podanego.
 *
 * @param img Zjęcie (cv::Mat) z którego chcemy wyodrębinić kolor.
 * @param rgb Kolor w formacie RGB reprezentowany przez (cv::Scalar) który chcemy wodrębinić.
 * @param lowerHueTolerance Dolna granica odcieniu koloru którego nie usuwamy.
 * @param lowerSaturationTolerance Dolna granica nasycenia koloru którego nie usuwamy.
 * @param lowerValueTolerance Dolna granica mocy światła białego koloru którego nie usuwamy.
 * @param upperHueTolerance Górna granica odcieniu koloru którego nie usuwamy.
 * @param upperSaturationTolerance Górna granica nasycenia koloru którego nie usuwamy.
 * @param upperValueTolerance Górna granica mocy światła białego koloru którego nie usuwamy.
 */
cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int lowerHueTolerance, int lowerSaturationTolerance, int lowerValueTolerance, int upperHueTolerance, int upperSaturationTolerance, int upperValueTolerance);

/**
 * @brief Umożliwia konwersje koloru z formatu RGB do HSV.
 *
 * Pobiera kolor (cv::Scalar) reprezentowany w formacie RGB i przekształca go do HSV.
 *
 * @param rgb Kolor w formacie RGB.
 *
 * @return (cv::Vec3b) reprezentujący format HSV
 */
cv::Vec3b convertRGBtoHSV(cv::Scalar rgb);

/**
 * @brief Przeprowadza przekształcenie morfologiczne MORPH_CLOSING na zdjęciu.
 *
 * Korzysta z morphologyEx, MORPH_CLOSING do przekształcenia zdjęcia. Usuwa dziury w liniach.
 *
 * @param image Zdjęcie które chcemy przekształcić (cv::Mat).
 * @param size Rozmiar elementu wykorzystwanego do przekształcenia morfologicznego.
 * @param element Kształt elementu (cv::Morph_Shapes)
 */
cv::Mat morphologyClosing(cv::Mat image, int size, int element); 

/**
 * @brief Przeprowadza rozszerzenie a następnie szkieletonizacje na zdjęciu.
 *
 * Korzysta z (cv::dialete) do rozszerzania, a do szkieletonizacji (cv::cv::ximgproc::THINNING_ZHANGSUEN).
 * Usuwa dzury w liniach, działa przez powiekszenie kształtów a nastepnie wykonuje szkieletonizacje.
 *
 * @param image Zjęcie które chcemy przekształcić (cv::Mat) 
 * @param size Rozmair elementu wykorzystwanego do (cv::dialete)
 * @param element Kształt elementu (cv::Morph_Shapes)
 */
cv::Mat skeletonization(cv::Mat image, int size, int element); 

/**
 * @brief Przeprowadza przekształcenie morfologiczne MORPH_OPENING na zdjęciu.
 *
 * Korzysta z morphologyEx, MORPH_OPENING do przekształcenia zdjęcia. Pozwala na usunięcię wad z zdjecia.
 *
 * @param image Zdjęcie które chcemy przeształcić (cv::Mat)
 * @param size Rozmair elementu wykorzystwanego do przekształcenia morfologicznego.
 */
cv::Mat morphologyOpening(cv::Mat image, int size);  
