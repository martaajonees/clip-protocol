<p align="center"> <img src="https://github.com/user-attachments/assets/6b8ba777-81d5-4411-93ba-8bb4359c89f9" alt="Logo" width="500"> </p>
<p align="center">
<img src="https://badgen.net/badge/license/MIT/orange?icon=github" alt="build badge">
<img src="https://badgen.net/badge/language/Python/yellow" alt="language badge">
<img src="https://badgen.net/badge/build/passing/green?icon=githubactions" alt="build badge">
<img src="https://badgen.net/pypi/v/clip-protocol" alt="PyPI version">
<img src="https://img.shields.io/pypi/pyversions/clip-protocol?color=red" alt="Python version supported">
<a href="https://martaajonees.github.io/Local_Privacy/src.html">
  <img src="https://img.shields.io/badge/docs-online-blueviolet" alt="documentation">
</a>
</p>

This repository contains an adaptation of differential privacy algorithms applied to learning analytics.
## Index
* [Project Description](#project-description)
* [Repository Structure](#repository-structure)
* [Online Execution](#online-execution)
* [Usage](#usage)
* [Documentation](#documentation)

## Project Description
Learning analytics involves collecting and analyzing data about learners to improve educational outcomes. However, this process raises concerns about the privacy of individual data. To address these concerns, this project implements differential privacy algorithms, which add controlled noise to data, ensuring individual privacy while maintaining the overall utility of the dataset. This approach aligns with recent advancements in safeguarding data privacy in learning analytics. 

In this project, we explore a privacy protocol for sketching with privacy considerations. The steps it follow

* **Setup**
* **Mask**
* **Agregation**
* **Estimation**


## Repository Structure
The repository is organized as follows:
```sh
Local_Privacy
┣ 📂 src
┣ ┣ 📂 clip_protocol
┃ ┃ ┣ 📂 count mean
┃ ┃ ┣ 📂 hadamard mean
┃ ┃ ┣ 📂 main
┃ ┃ ┃ ┣ setup.py
┃ ┃ ┃ ┣ mask.py
┃ ┃ ┃ ┣ agregate.py
┃ ┃ ┃ ┗ estimation.py
┃ ┗ ┗ 📂 utils
┗ 📂 tests
```
## Online Execution
You can execute the code online using Google Colab. Google Colab sessions are intended for individual users and have limitations such as session timeouts after periods of inactivity and maximum session durations. 

For **single-user dataset** scenarios, click this link to execute the method: [Execute in Google Colab (Single-User)](https://colab.research.google.com/drive/1dY1OSfRECHFBFYaX_5ToZy-KynjT_0z0?usp=sharing)

## Usage 
These methods are included in PyPI as you can view [here](https://pypi.org/project/clip-protocol/), and can be installed on your device with:
```sh
pip install clip-protocol
```
Once installed, you can execute the following commands to run the privacy adjustment methods.
### Setup
Use the following command:
```sh
setup -d <dataset>
```
- `dataset`: path to the input dataset (`.xlsx`) you want to setup for tests

Example:
```sh
setup -d /path/to/dataset.xlsx
```
### Mask
Use the following command:
```sh
mask -d <dataset>
```
- `dataset`: Path to the input dataset you want to privatize.
### Agregation
Use the following command:
```sh
agregate
```
### 
### Important Notes
- Ensure that the paths provided are correct, and that the necessary permissions are granted for writing to the output location.
- In the mask step, the output will be a new file `.csv` containing the privatized data.
  
## Documentation
The complete documentation for this project is available online. You can access it at the following link:
- [Project Documentation - Local Privacy in Learning Analytics](https://martaajonees.github.io/Local_Privacy/)

This documentation includes detailed explanations of the algorithms, methods, and the overall structure of the project.

## Authors
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/martaajonees"><img src="https://avatars.githubusercontent.com/u/100365874?v=4?s=100" width="100px;" alt="Marta Jones"/><br /><sub><b>Marta Jones</b></sub></a><br /><a href="https://github.com/martaajonees/Local_Privacy/commits?author=martaajonees" title="Code">💻</a></td>
       <td align="center" valign="top" width="14.28%"><a href="https://github.com/ichi91"><img src="https://avatars.githubusercontent.com/u/41892183?v=4?s=100" width="100px;" alt="Anailys Hernandez" style="border-radius: 50%"/><br /><sub><b>Anailys Hernandez</b></sub></a><br /><a href="https://github.com/ichi91/Local_Privacy/commits?author=ichi91" title="Method Designer">💡</a></td>
    </tr>
     
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

