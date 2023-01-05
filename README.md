# New-Debleeding-Algorithm-for-Image-colorization

This repossitory contains a Python implementation of the New Debleeding Colorization Algorithm.
Our proposed method is based on https://www.cs.huji.ac.il/w~yweiss/Colorization. 
We consider the intensity value difference and distance difference between the central pixel in the window and its neighbor pixels comprehensively. 
Combined with side window filtering, our algorithm significantly reduces the occurrence of colors bleeding at the edges of the colored image. 

## Run
The test images is located in the `test image` directory.
Run main.py to enjoy your colorization.

```bash
python main.py
```

## Sample results

Original                       | Scribbles                              | Result                          
:-------------:                | :-------------:                        | :-----:                         
![image]([test images/baby.bmp](https://raw.githubusercontent.com/Surge-Dan/New-Debleeding-Algorithm-for-Image-colorization/main/test%20images/baby.bmp))      | ![image]([test images/baby_marked.bmp](https://raw.githubusercontent.com/Surge-Dan/New-Debleeding-Algorithm-for-Image-colorization/main/test%20images/baby_marked.bmp))      | ![image]([result images/with SWF/baby.png](https://raw.githubusercontent.com/Surge-Dan/New-Debleeding-Algorithm-for-Image-colorization/main/result%20images/with%20SWF/baby.bmp))     
![image]([test images/glass.bmp](https://raw.githubusercontent.com/Surge-Dan/New-Debleeding-Algorithm-for-Image-colorization/main/test%20images/glass.bmp))   | ![image]([test images/glass_marked.bmp](https://raw.githubusercontent.com/Surge-Dan/New-Debleeding-Algorithm-for-Image-colorization/main/test%20images/glass_marked.bmp))   | ![image]([result images/with SWF/glass.png](https://raw.githubusercontent.com/Surge-Dan/New-Debleeding-Algorithm-for-Image-colorization/main/result%20images/with%20SWF/glass.bmp))  
![image]([test images/monaco.bmp](https://raw.githubusercontent.com/Surge-Dan/New-Debleeding-Algorithm-for-Image-colorization/main/test%20images/monaco.bmp))  | ![image]([test images/monaco_marked.bmp](https://raw.githubusercontent.com/Surge-Dan/New-Debleeding-Algorithm-for-Image-colorization/main/result%20images/with%20SWF/baby.bmp))  | ![image]([result images/with SWF/monaco.png](https://raw.githubusercontent.com/Surge-Dan/New-Debleeding-Algorithm-for-Image-colorization/main/result%20images/with%20SWF/monaco.bmp)) 
