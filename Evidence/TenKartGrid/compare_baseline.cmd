@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
cl /nologo /EHsc /std:c++17 /I Checkpoints\TenKartGrid\Source Evidence\TenKartGrid\compare_baseline.cpp Checkpoints\TenKartGrid\Source\KartTireModel.cpp /Fe:Evidence\TenKartGrid\baseline.exe /Fo:Evidence\TenKartGrid\ >nul
Evidence\TenKartGrid\baseline.exe
cl /nologo /EHsc /std:c++17 /I Source\Road_To_F1_New Evidence\TenKartGrid\compare_baseline.cpp Source\Road_To_F1_New\KartTireModel.cpp /Fe:Evidence\TenKartGrid\current.exe /Fo:Evidence\TenKartGrid\ >nul
Evidence\TenKartGrid\current.exe
