<h1 align="center"> Local Privacy in Learning Analytics </h1>

This repository contains an adaptation of differential privacy algorithms applied to learning analytics.
## Index
* [Project Description](#project-description)
* [Repository Structure](#repository-structure)
* [Online Execution](#online-execution)
* [Installation](#installation)
* [Documentation](#documentation)

## Project Description
Learning analytics involves collecting and analyzing data about learners to improve educational outcomes. However, this process raises concerns about the privacy of individual data. To address these concerns, this project implements differential privacy algorithms, which add controlled noise to data, ensuring individual privacy while maintaining the overall utility of the dataset. This approach aligns with recent advancements in safeguarding data privacy in learning analytics. 

In this project, we explore two local differential privacy (LDP) algorithms designed for sketching with privacy considerations:

* **Single-User Dataset Algorithm**: This algorithm is tailored for scenarios where data is collected from individual users. Each user's data is perturbed locally before aggregation, ensuring that their privacy is preserved without relying on a trusted central authority. Techniques such as randomized response and local perturbation are employed to achieve this. 

* **Multi-User Dataset Algorithm**: In situations involving data from multiple users, this algorithm aggregates the perturbed data to compute global statistics while preserving individual privacy. Methods like private sketching and frequency estimation are utilized to handle the complexities arising from multi-user data aggregation

For the **Single-User Dataset Algorithm**, the next figure provides a high-level overview of the proposal workflow. At the end, an interest third party could ask the server a query over the frequency of certain
events related to an individual. The estimation phase is simulated on the user side in
order to adjust the ratio between privacy and utility before sending the information to
the server. The algorithm first filters the information (Filter), then encodes the relevant
events extracted (Data Processing) in order to be received for the PLDP-CSM method.

<p align="center"> <img src="https://github.com/user-attachments/assets/2515e75a-5a84-4ea4-8bde-5422be6e5e41" alt="High-Level overview of the workflow"> </p>

Then, the Cont Sketch based Personalized-LDP (PLDP-CSM) enables the adjustment of the relation between
utility and privacy by iterating over data until the output of the simulator satisfies
the constraints of users. This part of the algorithm produces the privatize dataset,
which will be sent to the server.

<p align="center"> <img src="https://github.com/user-attachments/assets/706a966f-1c2b-4f16-83df-883b12ef8fe7" alt="Figuras Analysis"> </p>

## Repository Structure
```sh
Local_Privacy
│
├── data/                
│   ├── raw/             # Unprocessed data
│   ├── private/       # Data after privatizing
│
├── scripts/             
│   ├── preprocess.py    # Data preprocessing routines
│   ├── algorithms.py    # Implementation of differential privacy algorithms
│   ├── parameter_fitting.py    # Parameter tuning for algorithms
│
├── src/                 # Privacy code
│   ├── private_count_mean/          # Code for private count mean algorithms
│   ├── private_hadamard_count_mean/ # Code for private Hadamard count mean algorithms
│   ├── rappor/                      # Implementation of RAPPOR algorithm
│
├── requirements.txt     # List of Python dependencies
│
├── individual_method.py # Main file for the single-user dataset algorithm
│
├── general_method.py # Main file for the multi-user dataset algorithm
   
```
## Online Execution
You can execute the code online using Google Colab. Google Colab sessions are intended for individual users and have limitations such as session timeouts after periods of inactivity and maximum session durations. 

- For **single-user dataset** scenarios, click this link to execute the method: [Execute in Google Colab (Single-User)](https://colab.research.google.com/drive/1dY1OSfRECHFBFYaX_5ToZy-KynjT_0z0?usp=sharing)

- For **multi-user dataset** scenarios, click this link to execute the method: [Execute in Google Colab (Multi-User)](https://colab.research.google.com/drive/1zenZ2uTNYVNylNJ7ztIj5x_cIQVXP4HV?usp=sharing)
## Installation
[Ver en Pypi](https://pypi.org/project/privadjust/1.0.2/)
Follow these steps to set up and execute the methods:
1. **Install with pip**
   ```sh
   pip install privadjust
   ```
2. **Upload your dataset**. Place your dataset inside the data/raw directory.
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
5. **Run the methods**. Navigate to the src directory and execute the desired method:
   * For **single-user dataset** analysis:
     ```sh
     cd src
     python individual_method.py
     ```
    * For **multi-user dataset** analysis:
       ```sh
       cd src
       python general_method.py
       ```
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

