#pragma once

extern "C" __declspec(dllexport)
int CutStl(
    const char* inputPath,
    const char* outputA,
    const char* outputB,
    double planeX,
    double planeY,
    double planeZ,
    double planeD);
