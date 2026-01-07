using System;
using System.Runtime.InteropServices;

namespace StlCutter
{
    public static class StlCutter
    {
        [DllImport("StlCutterLib.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int CutStl(
            string inputPath,
            string outputA,
            string outputB,
            double planeX,
            double planeY,
            double planeZ,
            double planeD);
    }
}
