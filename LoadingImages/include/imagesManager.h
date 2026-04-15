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

/**
 * @brief Pozwala na połącznie zdjęć w jedno.
 *
 * Zdjęcia pokrywające się (na zakładkę) łaczy ze sobą zgodnie z formatem zdefiniowanym w konfiguracji.
 * 
 * @return Zjęcie (cv::Mat) scalone zdjęcie.
 * @param images Zdjęcia (cv::Mat) które zostaną połączone.
 * @param option Konfiguracja określająca w jakim formacie zostaną zdjęcia złączone
 */
cv::Mat connectAllImages(std::vector<cv::Mat> images, std::pair<int, int> option);

/**
 * @brief Lączy ze spobą dwa zdjęcia w poziomie, gdy znajdzie fragment pokrywający w obu zdjęciach.
 *
 * Do prawidłowego działania jest konieczność pokrycia między zdjęciami (zdjęcia na zakładkę), szukany jest
 * fragment prawego zdjęcia w lewym za pomocą (findPoint) następnie zdjęcia te są dopasowywane.
 *
 * @param left Zdjęcie (cv::Mat) do którego będziemy dopasowywać.
 * @param right Zdjęcie (cv::Mat) w którym znajdujemy punkt dopasowania.
 */
cv::Mat connectTwoImagesHorizontally(cv::Mat left, cv::Mat right);

/**
 * @brief Lączy ze spobą dwa zdjęcia w pionie, gdy znajdzie fragment pokrywający w obu zdjęciach.
 *
 * Do prawidłowego działania jest konieczność pokrycia między zdjęciami (zdjęcia na zakładkę), szukany jest
 * fragment prawego zdjęcia w lewym za pomocą (findPoint) następnie zdjęcia te są dopasowywane.
 *
 * @param left Zdjęcie (cv::Mat) do którego będziemy dopasowywać.
 * @param right Zdjęcie (cv::Mat) w którym znajdujemy punkt dopasowania.
 */
cv::Mat connectTwoImagesVertically(cv::Mat left, cv::Mat right);

/**
 * @brief Znajduje punkt w którym fragment prawego zdjęcia znajduje się w lewym.
 *
 * Fragment prawego zjdęcia który określony jest za pomocą tX, tY, tWidht, tHeight.
 * Jest szukany w lewym zdjęciu za pomoca (cv::matchTemplate)
 *
 * @return Punkt gdzie został znaleziony fragment.
 *
 * @param left Zdjęcie (cv::Mat)
 * @param right Zdjęcie (cv::Mat)
 * @param tX Określa współrzędną X dla fragmentu który będzie szukany w zdjęciu. 
 * @param tY Określa współrzędną Y dla fragmentu który będzie szukany w zdjęciu.
 * @param tWidht Określa długość fragmentu.
 * @param tHeight Określa wysokość fragmentu.
 */
cv::Point findPoint(cv::Mat left, cv::Mat right, int tX, int tY, int tWidht, int tHeight);

/**
 * @brief Usuwa wszystkie inne kolory ze zdjęcia nie pasujące do podanego.
 *
 * Na podstawie koloru (rgb) usuwa wszystkie kolory które nie pasują do podanego zakresu.
 *
 * @param img Zjdęcie (cv::Mat) z którego chcemy wyodrębinić kolor.
 * @param rgb Kolor w formacie RGB reprezentowany przez (cv::Scalar) który chcemy wodrębinić.
 * @param diff Zakres koloru którego nie będziemy usuwać.
 */
cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int diff);

/**
 * @brief Usuwa wszystkie inne kolory ze zdjęcia nie pasujące do podanego.
 *
 * Na podstawie koloru (rgb) usuwa wszystkie kolory które nie pasują do podanego zakresu, określonego przez
 * lowerDiff i upperDiff.
 *
 * @param img Zjdęcie (cv::Mat) z którego chcemy wyodrębinić kolor.
 * @param rgb Kolor w formacie RGB reprezentowany przez (cv::Scalar) który chcemy wodrębinić.
 * @param lowerDiff Dolna granica koloru którego nie będziemy usuwać.
 * @param upperDiff Górna granica koloru którego nie będziemy usuwać.
 */
cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int lowerDiff, int upperDiff);

/**
 * @brief Usuwa wszystkie inne kolory ze zdjęcia nie pasujące do podanego.
 *
 * Konweturje zjdecie do formatu HSV, następnie na podstawie wybrango koloru (rgb) usuwa wszystkie kolory
 * które nie pasują do podanego zakresu.
 *
 * @param img Zjęcie (cv::Mat) z którego chcemy wyodrębinić kolor.
 * @param rgb Kolor w formacie RGB reprezentowany przez (cv::Scalar) który chcemy wodrębinić.
 * @param hueTolerance Zakres nasycenia koloru którego nie usuwamy.
 * @param saturationTolerance Zakres odcieniu koloru którego nie usuwamy. 
 * @param valueTolerance Zakres mocy świtała białego koloru którego nie usuwamy.
 */
cv::Mat removeAllOtherColors(cv::Mat img, cv::Scalar rgb, int hueTolerance, int saturationTolerance, int valueTolerance);

/**
 * @brief Usuwa wszystkie inne kolory ze zdjęcia nie pasujące do podanego.
 * 
 * Konweturje zjdecie do formatu HSV, następnie na podstawie wybrango koloru (rgb) usuwa wszystkie koloru
 * które nie pasują do podanego zakresu.
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
