
#pragma once

#include "opencv2/core/mat.hpp"
#include "opencv2/core/types.hpp"
#include <vector>

/**
 * @stuct HueParameters
 * @brief Zawiera parametry HSV.
 */
struct HueParameters{
  int lowHue = 0, lowSaturation = 0, lowValue = 0;
  int highHue = 0, highSaturation = 0, highValue = 0;
};

/**
 * @class WindowManager
 * @brief Zarządza oknami wyświetlanymi w programie.
 *
 */
class WindowManager{
  public:
    cv::Mat img;
    cv::Scalar pickedColor;
    std::vector<cv::Mat> images;
    HueParameters hueParameters;
    cv::Scalar rgb;
    int height = 0;
    int basedHeight = 0;
    int scaleHeight = 1;
    int size = 1;
    int colorChosed = 1;
    bool drawMode = true;
    int morph_elem = 0;
    int morph_size = 0;

    /**
     * @brief Okno pozwalające na wybór koloru ze zjęcia.
     *
     * Wyświetla okno, za pomocą klikniecia pobierasz kolor i jego wartość RGB.
     * Następnie ta wartość zapisywana jest w (cv::Scalar rgb). 
     *
     * @param img Zdjęcie które chcesz wyświetlić i pobrać z niego kolor.
     */
    cv::Scalar pickColorWindow(cv::Mat &img);


    /**
     * @brief Okno pozwalające na wyodrębnienie koloru ze zdjęcia.
     *
     * Wyświetla okno w którym jesteś w stanie wyodrębinić wszystkie inne kolory.
     * Za pomocą suwaków określasz zakres na ile podobny kolor zostanie usuniety.
     *
     * @param images Vector zdjęć (cv::Mat) z których chcemy wyodrębinić kolor.
     * @param config Konfiguracja.
     * @param rgb Kolor który chcemy wyodrębinić.
     */
    std::vector<cv::Mat> removeColorWindow(std::vector<cv::Mat>& images, cv::Scalar rgb);

    /**
     * @brief Okno pozwalające na wyodrębnienie koloru ze zdjęcia.
     *
     * Wyświetla okno w którym jesteś w stanie wyodrębinić wszystkie inne kolory.
     * Za pomocą suwaków określasz zakres na ile podobny kolor zostanie usuniety.
     *
     * @param images Vector zdjęć (cv::Mat) z których chcemy wyodrębinić kolor.
     * @param config Konfiguracja.
     * @param rgb Kolor który chcemy wyodrębinić.
     */
    cv::Mat removeColorWindow(cv::Mat image, cv::Scalar rgb);


    /**
     * @brief Okno pozwalające na rysowanie po zdjęciu.
     *
     * Wyświetla okno w którym możemy poprawić błędy, które mogły się pojawić przy wyodrębinianiu koloru.
     * C - pozwala na zmiane koloru. Suwak pozwala na określenie rozmiaru pędzla.
     * 
     * @param img Zdjecie (cv::Mat) na którym chcemy rysować.
     * @param config Konfiguracja.
     */
    cv::Mat drawWindow(cv::Mat &img);

    /**
     * @brief Okno pozwalające na usuwanie braków w poziomicy.
     *
     * Wyświetla okno, w którym za pomoca skeletonize jesteśmy w stanie połączyć 'contour' w przypadku gdy,
     * między nimi znajduje się dziura.
     *
     * @param img Zjecie (cv::Mat) na którym chcemy przeprowadzić rozszerznie i szkieletonizacje.
     */
    cv::Mat fixGapsInContourWindow(cv::Mat img); 


    cv::Mat fixGapsInContourWindow2(cv::Mat img);

  private:

    static void getColor(int event, int x, int y, int, void* userdata);
    static void drawPixelWhite(int event, int x, int y, int, void* userdata);
    static void drawRectengle(cv::Mat& img, int x, int y, int size, int color);
    static void drawCircle(cv::Mat& img, int x, int y, int size, int color);
};
