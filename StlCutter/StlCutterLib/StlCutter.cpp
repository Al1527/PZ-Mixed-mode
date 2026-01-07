#include "StlCutter.h"
#include <vtkSTLReader.h>
#include <vtkSTLWriter.h>
#include <vtkSmartPointer.h>
#include <vtkPlane.h>
#include <vtkClipPolyData.h>
#include "pch.h"

int CutStl(
    const char* inputPath,
    const char* outputA,
    const char* outputB,
    double planeX,
    double planeY,
    double planeZ,
    double planeD)
{
    try
    {
        auto reader = vtkSmartPointer<vtkSTLReader>::New();
        reader->SetFileName(inputPath);
        reader->Update();

        auto plane = vtkSmartPointer<vtkPlane>::New();
        plane->SetNormal(planeX, planeY, planeZ);
        plane->SetOrigin(planeX * planeD, planeY * planeD, planeZ * planeD);

        auto clipInside = vtkSmartPointer<vtkClipPolyData>::New();
        clipInside->SetInputConnection(reader->GetOutputPort());
        clipInside->SetClipFunction(plane);
        clipInside->InsideOutOn();
        clipInside->Update();

        auto clipOutside = vtkSmartPointer<vtkClipPolyData>::New();
        clipOutside->SetInputConnection(reader->GetOutputPort());
        clipOutside->SetClipFunction(plane);
        clipOutside->InsideOutOff();
        clipOutside->Update();

        auto writerA = vtkSmartPointer<vtkSTLWriter>::New();
        writerA->SetFileName(outputA);
        writerA->SetInputData(clipInside->GetOutput());
        writerA->Write();

        auto writerB = vtkSmartPointer<vtkSTLWriter>::New();
        writerB->SetFileName(outputB);
        writerB->SetInputData(clipOutside->GetOutput());
        writerB->Write();

        return 0;
    }
    catch (...)
    {
        return -1;
    }
}
