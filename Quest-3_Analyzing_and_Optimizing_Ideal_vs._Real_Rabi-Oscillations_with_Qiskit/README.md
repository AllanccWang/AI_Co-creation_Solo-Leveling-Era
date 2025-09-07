# Goal
The primary goal of this quest is to develop and implement a strategy that optimizes noisy Rabi oscillations on a simulated quantum hardware, bringing them as close as possible to ideal, noise-free behavior. This involves understanding noise, characterizing its impact, and applying advanced techniques to mitigate it.

## Method 1: Machine Learning - Hyperparameter Optimization:
Approach: While direct pulse-level tuning isn't the primary focus, explore optimizing circuit-level parameters. Employ machine learning or optimization algorithms to discover an optimal sequence of Rx gate angles.
**Advanced Consideration: Investigate the insertion of additional gates for dynamic decoupling between Rx gates to enhance noise resistance.**

* Refer: [**Rabi_Oscillation_with_QOC**](https://github.com/AllanccWang/AI_Co-creation_Solo-Leveling-Era/blob/8ea58002eb914952654497df99cf6f309bf0c6dd/Quest-3_Analyzing_and_Optimizing_Ideal_vs._Real_Rabi-Oscillations_with_Qiskit/Rabi_Oscillation_with_QOC.ipynb)

## Method 2: Machine Learning - Data Analysis & Predictive Modeling:
Approach: Analyze the data collected from Side Quest 2 using machine learning models.
**Objective: Develop a predictive model that learns the specific noise patterns of FakePerth to forecast how noise impacts measurement outcomes at different rotation angles. This will deepen your understanding of the noise's fundamental sources.**

* Refer: [**Rabi_Oscillation_Modeling_with_a_Regression Model**](https://github.com/AllanccWang/AI_Co-creation_Solo-Leveling-Era/blob/543bc4e9fc5c13e2182e1f3b8fa66fdd87aca89c/Quest-3_Analyzing_and_Optimizing_Ideal_vs._Real_Rabi-Oscillations_with_Qiskit/Rabi_Oscillation_Modeling_with_a_Regression%20Model.ipynb)
