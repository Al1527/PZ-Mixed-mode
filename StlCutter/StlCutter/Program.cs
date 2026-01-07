using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace StlCutter
{
    internal class Program
    {
        static void Main()
        {
            int result = StlCutter.CutStl(
                "model.stl",
                "partA.stl",
                "partB.stl",
                0, 1, 0, 0); // płaszczyzna Y=0

            Console.WriteLine("Result: " + result);
        }
    }

}
